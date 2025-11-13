package models

import "time"

// CreateMatchRequest DTO para crear una partida
type CreateMatchRequest struct {
	TournamentID uint       `json:"tournament_id" validate:"required"`
	Round        int        `json:"round" validate:"required,min=1"`
	MatchNumber  int        `json:"match_number" validate:"required,min=1"`
	Player1ID    *uint      `json:"player1_id"`
	Player2ID    *uint      `json:"player2_id"`
	ScheduledAt  *time.Time `json:"scheduled_at"`
	Notes        string     `json:"notes"`
}

// UpdateMatchRequest DTO para actualizar una partida
type UpdateMatchRequest struct {
	Player1ID    *uint        `json:"player1_id"`
	Player2ID    *uint        `json:"player2_id"`
	Player1Score *int         `json:"player1_score" validate:"omitempty,min=0"`
	Player2Score *int         `json:"player2_score" validate:"omitempty,min=0"`
	Status       *MatchStatus `json:"status"`
	ScheduledAt  *time.Time   `json:"scheduled_at"`
	Notes        *string      `json:"notes"`
}

// StartMatchRequest DTO para iniciar una partida
type StartMatchRequest struct {
	// Podría incluir configuraciones adicionales
}

// CompleteMatchRequest DTO para completar una partida
type CompleteMatchRequest struct {
	Player1Score int    `json:"player1_score" validate:"required,min=0"`
	Player2Score int    `json:"player2_score" validate:"required,min=0"`
	WinnerID     uint   `json:"winner_id" validate:"required"`
	Notes        string `json:"notes"`
}

// RecordResultRequest DTO para registrar un resultado detallado
type RecordResultRequest struct {
	PlayerID uint                   `json:"player_id" validate:"required"`
	Score    int                    `json:"score" validate:"required,min=0"`
	IsWinner bool                   `json:"is_winner"`
	Stats    map[string]interface{} `json:"stats"` // Estadísticas en formato libre
	Notes    string                 `json:"notes"`
}

// MatchResponse DTO para respuesta de partida
type MatchResponse struct {
	ID           uint        `json:"id"`
	TournamentID uint        `json:"tournament_id"`
	Round        int         `json:"round"`
	MatchNumber  int         `json:"match_number"`
	Player1ID    *uint       `json:"player1_id"`
	Player2ID    *uint       `json:"player2_id"`
	WinnerID     *uint       `json:"winner_id"`
	Player1Score int         `json:"player1_score"`
	Player2Score int         `json:"player2_score"`
	Status       MatchStatus `json:"status"`
	ScheduledAt  *time.Time  `json:"scheduled_at"`
	StartedAt    *time.Time  `json:"started_at"`
	CompletedAt  *time.Time  `json:"completed_at"`
	Notes        string      `json:"notes"`
	CreatedAt    time.Time   `json:"created_at"`
	UpdatedAt    time.Time   `json:"updated_at"`
}

// MatchListResponse DTO para listar partidas con paginación
type MatchListResponse struct {
	Matches    []MatchResponse `json:"matches"`
	Total      int64           `json:"total"`
	Page       int             `json:"page"`
	PageSize   int             `json:"page_size"`
	TotalPages int             `json:"total_pages"`
}

// ResultResponse DTO para respuesta de resultado
type ResultResponse struct {
	ID        uint                   `json:"id"`
	MatchID   uint                   `json:"match_id"`
	PlayerID  uint                   `json:"player_id"`
	Score     int                    `json:"score"`
	IsWinner  bool                   `json:"is_winner"`
	Stats     map[string]interface{} `json:"stats"`
	Notes     string                 `json:"notes"`
	CreatedAt time.Time              `json:"created_at"`
	UpdatedAt time.Time              `json:"updated_at"`
}
