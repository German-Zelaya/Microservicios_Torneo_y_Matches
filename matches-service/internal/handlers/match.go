package handlers

import (
	"strconv"

	"github.com/gofiber/fiber/v2"

	"matches-service/internal/models"
	"matches-service/internal/services"
)

type MatchHandler struct {
	service *services.MatchService
}

func NewMatchHandler() *MatchHandler {
	return &MatchHandler{
		service: services.NewMatchService(),
	}
}

// CreateMatch godoc
// @Summary Crear una nueva partida
// @Tags Matches
// @Accept json
// @Produce json
// @Param match body models.CreateMatchRequest true "Datos de la partida"
// @Success 201 {object} models.MatchResponse
// @Router /api/v1/matches [post]
func (h *MatchHandler) CreateMatch(c *fiber.Ctx) error {
	var req models.CreateMatchRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Datos inválidos",
		})
	}

	match, err := h.service.CreateMatch(&req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.Status(201).JSON(h.service.ToResponse(match))
}

// GetMatches godoc
// @Summary Listar partidas
// @Tags Matches
// @Produce json
// @Param page query int false "Número de página" default(1)
// @Param page_size query int false "Tamaño de página" default(10)
// @Param tournament_id query int false "Filtrar por torneo"
// @Param status query string false "Filtrar por estado"
// @Success 200 {object} models.MatchListResponse
// @Router /api/v1/matches [get]
func (h *MatchHandler) GetMatches(c *fiber.Ctx) error {
	// Parsear parámetros de paginación
	page, _ := strconv.Atoi(c.Query("page", "1"))
	pageSize, _ := strconv.Atoi(c.Query("page_size", "10"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 10
	}

	// Parsear filtros opcionales
	var tournamentID *uint
	if tid := c.Query("tournament_id"); tid != "" {
		if id, err := strconv.ParseUint(tid, 10, 32); err == nil {
			uidVal := uint(id)
			tournamentID = &uidVal
		}
	}

	var status *models.MatchStatus
	if s := c.Query("status"); s != "" {
		statusVal := models.MatchStatus(s)
		status = &statusVal
	}

	matches, total, err := h.service.GetMatches(page, pageSize, tournamentID, status)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	response := h.service.BuildListResponse(matches, total, page, pageSize)
	return c.JSON(response)
}

// GetMatch godoc
// @Summary Obtener una partida por ID
// @Tags Matches
// @Produce json
// @Param id path int true "ID de la partida"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id} [get]
func (h *MatchHandler) GetMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	match, err := h.service.GetMatchByID(uint(id))
	if err != nil {
		return c.Status(404).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// UpdateMatch godoc
// @Summary Actualizar una partida
// @Tags Matches
// @Accept json
// @Produce json
// @Param id path int true "ID de la partida"
// @Param match body models.UpdateMatchRequest true "Datos a actualizar"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id} [put]
func (h *MatchHandler) UpdateMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	var req models.UpdateMatchRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Datos inválidos",
		})
	}

	match, err := h.service.UpdateMatch(uint(id), &req)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// DeleteMatch godoc
// @Summary Eliminar una partida
// @Tags Matches
// @Param id path int true "ID de la partida"
// @Success 200 {object} map[string]string
// @Router /api/v1/matches/{id} [delete]
func (h *MatchHandler) DeleteMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	if err := h.service.DeleteMatch(uint(id)); err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(fiber.Map{
		"message": "Partida eliminada correctamente",
	})
}

// StartMatch godoc
// @Summary Iniciar una partida
// @Tags Matches
// @Produce json
// @Param id path int true "ID de la partida"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id}/start [patch]
func (h *MatchHandler) StartMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	match, err := h.service.StartMatch(uint(id))
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// CompleteMatch godoc
// @Summary Completar una partida y registrar ganador
// @Tags Matches
// @Accept json
// @Produce json
// @Param id path int true "ID de la partida"
// @Param result body models.CompleteMatchRequest true "Resultado de la partida"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id}/complete [patch]
func (h *MatchHandler) CompleteMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	var req models.CompleteMatchRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Datos inválidos",
		})
	}

	match, err := h.service.CompleteMatch(uint(id), &req)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// CancelMatch godoc
// @Summary Cancelar una partida
// @Tags Matches
// @Accept json
// @Produce json
// @Param id path int true "ID de la partida"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id}/cancel [patch]
func (h *MatchHandler) CancelMatch(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	var body struct {
		Reason string `json:"reason"`
	}
	c.BodyParser(&body)

	match, err := h.service.CancelMatch(uint(id), body.Reason)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// ReportResult godoc
// @Summary Reportar resultado de una partida
// @Tags Matches
// @Accept json
// @Produce json
// @Param id path int true "ID de la partida"
// @Param result body models.ReportResultRequest true "Resultado de la partida"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id}/result [post]
func (h *MatchHandler) ReportResult(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	var req models.ReportResultRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Datos inválidos",
		})
	}

	match, err := h.service.ReportResult(uint(id), &req)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}

// ValidateResult godoc
// @Summary Validar resultado reportado (referee/admin)
// @Tags Matches
// @Accept json
// @Produce json
// @Param id path int true "ID de la partida"
// @Param validation body models.ValidateResultRequest true "Validación del resultado"
// @Success 200 {object} models.MatchResponse
// @Router /api/v1/matches/{id}/validate [put]
func (h *MatchHandler) ValidateResult(c *fiber.Ctx) error {
	id, err := strconv.ParseUint(c.Params("id"), 10, 32)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "ID inválido",
		})
	}

	var req models.ValidateResultRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Datos inválidos",
		})
	}

	match, err := h.service.ValidateResult(uint(id), &req)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return c.JSON(h.service.ToResponse(match))
}
