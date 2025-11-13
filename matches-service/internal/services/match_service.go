package services

import (
	"errors"
	"fmt"
	"math"
	"time"

	"gorm.io/gorm"

	"matches-service/internal/cache"
	"matches-service/internal/database"
	"matches-service/internal/messaging"
	"matches-service/internal/models"
)

// MatchService maneja la lógica de negocio de partidas
type MatchService struct{}

// NewMatchService crea una nueva instancia del servicio
func NewMatchService() *MatchService {
	return &MatchService{}
}

// CreateMatch crea una nueva partida
func (s *MatchService) CreateMatch(req *models.CreateMatchRequest) (*models.Match, error) {
	match := &models.Match{
		TournamentID: req.TournamentID,
		Round:        req.Round,
		MatchNumber:  req.MatchNumber,
		Player1ID:    req.Player1ID,
		Player2ID:    req.Player2ID,
		ScheduledAt:  req.ScheduledAt,
		Notes:        req.Notes,
		Status:       models.MatchStatusScheduled,
		Player1Score: 0,
		Player2Score: 0,
	}

	if err := database.PostgresDB.Create(match).Error; err != nil {
		return nil, fmt.Errorf("error al crear partida: %w", err)
	}

	// Invalidar caché de listas
	cache.InvalidateMatchListCache()

	// Publicar evento
	matchData := s.ToMap(match)
	messaging.PublishMatchCreated(matchData)

	return match, nil
}

// GetMatchByID obtiene una partida por su ID (con caché)
func (s *MatchService) GetMatchByID(id uint) (*models.Match, error) {
	// Intentar obtener del caché
	cacheKey := cache.MatchCacheKey(id)
	var match models.Match

	err := cache.GetJSON(cacheKey, &match)
	if err == nil {
		// Encontrado en caché
		return &match, nil
	}

	// No está en caché o error, consultar BD
	if err := database.PostgresDB.First(&match, id).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, fmt.Errorf("partida con ID %d no encontrada", id)
		}
		return nil, err
	}

	// Guardar en caché (5 minutos)
	cache.SetJSON(cacheKey, &match, 5*time.Minute)

	return &match, nil
}

// GetMatches obtiene una lista de partidas con filtros
func (s *MatchService) GetMatches(page, pageSize int, tournamentID *uint, status *models.MatchStatus) ([]models.Match, int64, error) {
	var matches []models.Match
	var total int64

	query := database.PostgresDB.Model(&models.Match{})

	// Aplicar filtros
	if tournamentID != nil {
		query = query.Where("tournament_id = ?", *tournamentID)
	}
	if status != nil {
		query = query.Where("status = ?", *status)
	}

	// Contar total
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// Aplicar paginación
	offset := (page - 1) * pageSize
	if err := query.Order("round ASC, match_number ASC").
		Offset(offset).
		Limit(pageSize).
		Find(&matches).Error; err != nil {
		return nil, 0, err
	}

	return matches, total, nil
}

// UpdateMatch actualiza una partida
func (s *MatchService) UpdateMatch(id uint, req *models.UpdateMatchRequest) (*models.Match, error) {
	match, err := s.GetMatchByID(id)
	if err != nil {
		return nil, err
	}

	// Actualizar campos si están presentes
	updates := make(map[string]interface{})

	if req.Player1ID != nil {
		updates["player1_id"] = req.Player1ID
	}
	if req.Player2ID != nil {
		updates["player2_id"] = req.Player2ID
	}
	if req.Player1Score != nil {
		updates["player1_score"] = *req.Player1Score
	}
	if req.Player2Score != nil {
		updates["player2_score"] = *req.Player2Score
	}
	if req.Status != nil {
		updates["status"] = *req.Status
	}
	if req.ScheduledAt != nil {
		updates["scheduled_at"] = req.ScheduledAt
	}
	if req.Notes != nil {
		updates["notes"] = *req.Notes
	}

	if len(updates) > 0 {
		if err := database.PostgresDB.Model(match).Updates(updates).Error; err != nil {
			return nil, fmt.Errorf("error al actualizar partida: %w", err)
		}
	}

	return match, nil
}

// DeleteMatch elimina una partida (soft delete)
func (s *MatchService) DeleteMatch(id uint) error {
	match, err := s.GetMatchByID(id)
	if err != nil {
		return err
	}

	if err := database.PostgresDB.Delete(match).Error; err != nil {
		return fmt.Errorf("error al eliminar partida: %w", err)
	}

	return nil
}

// StartMatch inicia una partida
func (s *MatchService) StartMatch(id uint) (*models.Match, error) {
	match, err := s.GetMatchByID(id)
	if err != nil {
		return nil, err
	}

	// Validar que se puede iniciar
	if !match.CanStart() {
		return nil, errors.New("la partida no puede iniciar: verifica que esté programada y tenga ambos jugadores")
	}

	now := time.Now()
	match.Status = models.MatchStatusInProgress
	match.StartedAt = &now

	if err := database.PostgresDB.Save(match).Error; err != nil {
		return nil, fmt.Errorf("error al iniciar partida: %w", err)
	}

	// Invalidar caché
	cache.InvalidateMatchCache(id)
	cache.InvalidateMatchListCache()

	// Publicar evento
	matchData := s.ToMap(match)
	messaging.PublishMatchStarted(matchData)

	return match, nil
}

// CompleteMatch completa una partida y registra el ganador
func (s *MatchService) CompleteMatch(id uint, req *models.CompleteMatchRequest) (*models.Match, error) {
	match, err := s.GetMatchByID(id)
	if err != nil {
		return nil, err
	}

	// Validar que se puede completar
	if !match.CanComplete() {
		return nil, errors.New("la partida debe estar en progreso para completarse")
	}

	// Validar que el ganador es uno de los jugadores
	if match.Player1ID == nil || match.Player2ID == nil {
		return nil, errors.New("la partida debe tener ambos jugadores asignados")
	}
	if req.WinnerID != *match.Player1ID && req.WinnerID != *match.Player2ID {
		return nil, errors.New("el ganador debe ser uno de los jugadores de la partida")
	}

	// Validar puntuaciones
	if req.Player1Score == req.Player2Score {
		return nil, errors.New("no puede haber empate, debe haber un ganador")
	}

	now := time.Now()
	match.Status = models.MatchStatusCompleted
	match.CompletedAt = &now
	match.Player1Score = req.Player1Score
	match.Player2Score = req.Player2Score
	match.WinnerID = &req.WinnerID
	if req.Notes != "" {
		match.Notes = req.Notes
	}

	if err := database.PostgresDB.Save(match).Error; err != nil {
		return nil, fmt.Errorf("error al completar partida: %w", err)
	}

	// Invalidar caché
	cache.InvalidateMatchCache(id)
	cache.InvalidateMatchListCache()

	// Publicar evento
	matchData := s.ToMap(match)
	messaging.PublishMatchCompleted(matchData)

	return match, nil
}

// CancelMatch cancela una partida
func (s *MatchService) CancelMatch(id uint, reason string) (*models.Match, error) {
	match, err := s.GetMatchByID(id)
	if err != nil {
		return nil, err
	}

	if match.Status == models.MatchStatusCompleted {
		return nil, errors.New("no se puede cancelar una partida completada")
	}

	match.Status = models.MatchStatusCancelled
	if reason != "" {
		match.Notes = reason
	}

	if err := database.PostgresDB.Save(match).Error; err != nil {
		return nil, fmt.Errorf("error al cancelar partida: %w", err)
	}

	return match, nil
}

// ToResponse convierte un Match a MatchResponse
func (s *MatchService) ToResponse(match *models.Match) *models.MatchResponse {
	return &models.MatchResponse{
		ID:           match.ID,
		TournamentID: match.TournamentID,
		Round:        match.Round,
		MatchNumber:  match.MatchNumber,
		Player1ID:    match.Player1ID,
		Player2ID:    match.Player2ID,
		WinnerID:     match.WinnerID,
		Player1Score: match.Player1Score,
		Player2Score: match.Player2Score,
		Status:       match.Status,
		ScheduledAt:  match.ScheduledAt,
		StartedAt:    match.StartedAt,
		CompletedAt:  match.CompletedAt,
		Notes:        match.Notes,
		CreatedAt:    match.CreatedAt,
		UpdatedAt:    match.UpdatedAt,
	}
}

// BuildListResponse construye una respuesta de lista con paginación
func (s *MatchService) BuildListResponse(matches []models.Match, total int64, page, pageSize int) *models.MatchListResponse {
	matchResponses := make([]models.MatchResponse, len(matches))
	for i, match := range matches {
		matchResponses[i] = *s.ToResponse(&match)
	}

	totalPages := int(math.Ceil(float64(total) / float64(pageSize)))

	return &models.MatchListResponse{
		Matches:    matchResponses,
		Total:      total,
		Page:       page,
		PageSize:   pageSize,
		TotalPages: totalPages,
	}
}

// ToMap convierte un Match a map para eventos
func (s *MatchService) ToMap(match *models.Match) map[string]interface{} {
	data := map[string]interface{}{
		"id":            match.ID,
		"tournament_id": match.TournamentID,
		"round":         match.Round,
		"match_number":  match.MatchNumber,
		"player1_score": match.Player1Score,
		"player2_score": match.Player2Score,
		"status":        string(match.Status),
		"created_at":    match.CreatedAt,
		"updated_at":    match.UpdatedAt,
	}

	if match.Player1ID != nil {
		data["player1_id"] = *match.Player1ID
	}
	if match.Player2ID != nil {
		data["player2_id"] = *match.Player2ID
	}
	if match.WinnerID != nil {
		data["winner_id"] = *match.WinnerID
	}
	if match.ScheduledAt != nil {
		data["scheduled_at"] = *match.ScheduledAt
	}
	if match.StartedAt != nil {
		data["started_at"] = *match.StartedAt
	}
	if match.CompletedAt != nil {
		data["completed_at"] = *match.CompletedAt
	}

	return data
}
