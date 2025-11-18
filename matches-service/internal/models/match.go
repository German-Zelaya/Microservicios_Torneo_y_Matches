package models

import (
	"time"

	"gorm.io/gorm"
)

// MatchStatus representa el estado de una partida
type MatchStatus string

const (
	MatchStatusScheduled         MatchStatus = "scheduled"          // Programada
	MatchStatusInProgress        MatchStatus = "in_progress"        // En progreso
	MatchStatusPendingValidation MatchStatus = "pending_validation" // Esperando validación
	MatchStatusCompleted         MatchStatus = "completed"          // Completada
	MatchStatusCancelled         MatchStatus = "cancelled"          // Cancelada
)

// Match representa una partida dentro de un torneo
type Match struct {
	ID           uint `gorm:"primarykey" json:"id"`
	TournamentID uint `gorm:"not null;index" json:"tournament_id"` // Referencia al torneo
	Round        int  `gorm:"not null" json:"round"`               // Ronda (1, 2, 3... final)
	MatchNumber  int  `gorm:"not null" json:"match_number"`        // Número de partida en la ronda

	// Participantes (UUIDs como strings)
	Player1ID *string `gorm:"type:varchar(36);index" json:"player1_id"` // UUID del jugador/equipo 1
	Player2ID *string `gorm:"type:varchar(36);index" json:"player2_id"` // UUID del jugador/equipo 2
	WinnerID  *string `gorm:"type:varchar(36);index" json:"winner_id"`  // UUID del ganador

	// Puntuaciones
	Player1Score int `gorm:"default:0" json:"player1_score"`
	Player2Score int `gorm:"default:0" json:"player2_score"`

	// Estado y fechas
	Status      MatchStatus `gorm:"type:varchar(20);not null;default:'scheduled';index" json:"status"`
	ScheduledAt *time.Time  `json:"scheduled_at"` // Cuándo está programada
	StartedAt   *time.Time  `json:"started_at"`   // Cuándo inició
	CompletedAt *time.Time  `json:"completed_at"` // Cuándo terminó

	// Metadata
	Notes string `gorm:"type:text" json:"notes"` // Notas adicionales

	// Timestamps
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"` // Soft delete
}

// TableName especifica el nombre de la tabla
func (Match) TableName() string {
	return "matches"
}

// BeforeCreate hook que se ejecuta antes de crear
func (m *Match) BeforeCreate(tx *gorm.DB) error {
	// Validaciones adicionales si es necesario
	return nil
}

// IsCompleted verifica si la partida está completada
func (m *Match) IsCompleted() bool {
	return m.Status == MatchStatusCompleted
}

// HasPlayers verifica si ambos jugadores están asignados
func (m *Match) HasPlayers() bool {
	return m.Player1ID != nil && m.Player2ID != nil
}

// CanStart verifica si la partida puede iniciar
func (m *Match) CanStart() bool {
	return m.Status == MatchStatusScheduled && m.HasPlayers()
}

// CanComplete verifica si la partida puede completarse
func (m *Match) CanComplete() bool {
	return m.Status == MatchStatusInProgress
}

// CanReportResult verifica si se puede reportar un resultado
func (m *Match) CanReportResult() bool {
	return m.Status == MatchStatusInProgress
}

// CanValidate verifica si la partida puede ser validada
func (m *Match) CanValidate() bool {
	return m.Status == MatchStatusPendingValidation
}
