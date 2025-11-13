from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.database.session import get_db
from app.schemas.tournament import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentListResponse
)
from app.services.tournament_service import TournamentService
from app.models.tournament import TournamentStatus

router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"]
)


@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    tournament: TournamentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo torneo.
    
    - **name**: Nombre del torneo (3-200 caracteres)
    - **game**: Nombre del videojuego (2-100 caracteres)
    - **description**: Descripción opcional (máx. 1000 caracteres)
    - **max_participants**: Máximo de participantes (2-1000, default: 16)
    - **registration_start**: Fecha de inicio de inscripciones (opcional)
    - **registration_end**: Fecha de fin de inscripciones (opcional)
    - **tournament_start**: Fecha de inicio del torneo (opcional)
    - **tournament_end**: Fecha de fin del torneo (opcional)
    """
    return TournamentService.create_tournament(db, tournament)


@router.get("/", response_model=TournamentListResponse)
async def get_tournaments(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    game: Optional[str] = Query(None, description="Filtrar por juego"),
    status: Optional[TournamentStatus] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los torneos con paginación y filtros opcionales.
    
    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de resultados por página (default: 10, máx: 100)
    - **game**: Filtrar por nombre del juego
    - **status**: Filtrar por estado (pending, registration, in_progress, completed, cancelled)
    """
    skip = (page - 1) * page_size
    
    tournaments, total = TournamentService.get_tournaments(
        db=db,
        skip=skip,
        limit=page_size,
        game=game,
        status_filter=status
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return TournamentListResponse(
        tournaments=tournaments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un torneo específico por su ID.
    Este endpoint usa caché de Redis para mejorar el rendimiento.
    """
    tournament_data = TournamentService.get_tournament_cached(db, tournament_id)
    return tournament_data


@router.put("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    tournament: TournamentUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un torneo existente.
    
    Todos los campos son opcionales. Solo se actualizarán los campos enviados.
    """
    return TournamentService.update_tournament(db, tournament_id, tournament)


@router.patch("/{tournament_id}/status", response_model=TournamentResponse)
async def change_tournament_status(
    tournament_id: int,
    new_status: TournamentStatus,
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de un torneo.
    
    Estados disponibles:
    - **pending**: Pendiente
    - **registration**: Abierto a inscripciones
    - **in_progress**: En curso
    - **completed**: Finalizado
    - **cancelled**: Cancelado
    """
    return TournamentService.change_status(db, tournament_id, new_status)


@router.delete("/{tournament_id}", status_code=status.HTTP_200_OK)
async def delete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un torneo.
    """
    return TournamentService.delete_tournament(db, tournament_id)