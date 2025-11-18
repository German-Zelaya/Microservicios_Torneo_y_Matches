from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from app.models.tournament import TournamentStatus, TournamentType


class TournamentBase(BaseModel):
    """Schema base con campos comunes"""
    name: str = Field(..., min_length=3, max_length=200, description="Nombre del torneo")
    game: str = Field(..., min_length=2, max_length=100, description="Nombre del videojuego")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del torneo")
    max_participants: int = Field(default=16, ge=2, le=1000, description="Máximo de participantes")
    tournament_type: TournamentType = Field(default=TournamentType.INDIVIDUAL, description="Tipo de torneo: individual (1v1) o team (equipos)")
    
    registration_start: Optional[datetime] = Field(None, description="Inicio de inscripciones")
    registration_end: Optional[datetime] = Field(None, description="Fin de inscripciones")
    tournament_start: Optional[datetime] = Field(None, description="Inicio del torneo")
    tournament_end: Optional[datetime] = Field(None, description="Fin del torneo")
    
    @field_validator('name', 'game')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Valida que los campos no estén vacíos"""
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip()


class TournamentCreate(TournamentBase):
    """Schema para crear un torneo"""
    pass


class TournamentUpdate(BaseModel):
    """Schema para actualizar un torneo (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    game: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    max_participants: Optional[int] = Field(None, ge=2, le=1000)
    tournament_type: Optional[TournamentType] = None
    status: Optional[TournamentStatus] = None
    
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    tournament_start: Optional[datetime] = None
    tournament_end: Optional[datetime] = None


class TournamentResponse(TournamentBase):
    """Schema para respuestas de torneos"""
    id: int
    current_participants: int
    tournament_type: TournamentType
    status: TournamentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Permite crear desde modelos SQLAlchemy


class TournamentListResponse(BaseModel):
    """Schema para listar torneos con paginación"""
    tournaments: list[TournamentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StartTournamentRequest(BaseModel):
    """Schema para iniciar un torneo y generar bracket"""
    participant_ids: List[int] = Field(..., min_length=2, description="Lista de IDs de participantes")
    
    @field_validator('participant_ids')
    @classmethod
    def validate_participants(cls, v: List[int]) -> List[int]:
        """Valida que haya participantes únicos"""
        if len(v) != len(set(v)):
            raise ValueError("Los IDs de participantes deben ser únicos")
        return v


class BracketInfoResponse(BaseModel):
    """Schema para información del bracket"""
    tournament_id: int
    total_participants: int
    total_rounds: int
    first_round_matches: int
    matches_generated: int
    status: str