from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database.session import Base


class TournamentStatus(str, enum.Enum):
    """Estados posibles de un torneo"""
    PENDING = "pending"           # Pendiente, aún no comienza
    REGISTRATION = "registration" # Abierto a inscripciones
    IN_PROGRESS = "in_progress"   # En curso
    COMPLETED = "completed"       # Finalizado
    CANCELLED = "cancelled"       # Cancelado


class Tournament(Base):
    """
    Modelo de Torneo.
    
    Representa un torneo de eSports con toda su información básica.
    """
    __tablename__ = "tournaments"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    game = Column(String(100), nullable=False, index=True)  # Ej: "League of Legends", "CS:GO"
    description = Column(String(1000), nullable=True)
    
    # Configuración del torneo
    max_participants = Column(Integer, nullable=False, default=16)
    current_participants = Column(Integer, nullable=False, default=0)
    
    # Estado y fechas
    status = Column(
        SQLEnum(TournamentStatus),
        nullable=False,
        default=TournamentStatus.PENDING,
        index=True
    )
    
    # Timestamps
    registration_start = Column(DateTime(timezone=True), nullable=True)
    registration_end = Column(DateTime(timezone=True), nullable=True)
    tournament_start = Column(DateTime(timezone=True), nullable=True)
    tournament_end = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name='{self.name}', game='{self.game}', status='{self.status}')>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "name": self.name,
            "game": self.game,
            "description": self.description,
            "max_participants": self.max_participants,
            "current_participants": self.current_participants,
            "status": self.status.value if self.status else None,
            "registration_start": self.registration_start.isoformat() if self.registration_start else None,
            "registration_end": self.registration_end.isoformat() if self.registration_end else None,
            "tournament_start": self.tournament_start.isoformat() if self.tournament_start else None,
            "tournament_end": self.tournament_end.isoformat() if self.tournament_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }