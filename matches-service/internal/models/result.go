package models

import (
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// Result representa el resultado detallado de un jugador en una partida
type Result struct {
	ID       uint `gorm:"primarykey" json:"id"`
	MatchID  uint `gorm:"not null;index" json:"match_id"`  // Referencia a la partida
	PlayerID uint `gorm:"not null;index" json:"player_id"` // ID del jugador

	// Puntuación y estadísticas básicas
	Score    int  `gorm:"not null;default:0" json:"score"`
	IsWinner bool `gorm:"default:false" json:"is_winner"`

	// Estadísticas detalladas (almacenadas como JSON)
	Stats datatypes.JSON `gorm:"type:jsonb" json:"stats"`
	// Ejemplo de Stats:
	// {
	//   "kills": 15,
	//   "deaths": 8,
	//   "assists": 12,
	//   "accuracy": 65.5,
	//   "headshots": 7,
	//   "damage_dealt": 3500
	// }

	// Metadata
	Notes string `gorm:"type:text" json:"notes"`

	// Timestamps
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// TableName especifica el nombre de la tabla
func (Result) TableName() string {
	return "results"
}
