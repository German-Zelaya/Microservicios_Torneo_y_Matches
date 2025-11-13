from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.models.tournament import TournamentStatus


class TournamentBase(BaseModel):
    """Schema base con campos comunes"""
    name: str = Field(..., min_length=3, max_length=200, description="Nombre del torneo")
    game: str = Field(..., min_length=2, max_length=100, description="Nombre del videojuego")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del torneo")
    max_participants: int = Field(default=16, ge=2, le=1000, description="Máximo de participantes")
    
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
    status: Optional[TournamentStatus] = None
    
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    tournament_start: Optional[datetime] = None
    tournament_end: Optional[datetime] = None


class TournamentResponse(TournamentBase):
    """Schema para respuestas de torneos"""
    id: int
    current_participants: int
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