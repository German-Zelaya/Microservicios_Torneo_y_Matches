from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException, status
import logging

from app.models.tournament import Tournament, TournamentStatus
from app.schemas.tournament import TournamentCreate, TournamentUpdate
from app.cache.redis_client import redis_client

logger = logging.getLogger(__name__)


class TournamentService:
    """Servicio para manejar la lógica de negocio de torneos"""
    
    # Constantes para claves de caché
    CACHE_PREFIX = "tournament"
    CACHE_TTL = 300  # 5 minutos
    
    @staticmethod
    def _get_cache_key(tournament_id: int) -> str:
        """Genera la clave de caché para un torneo"""
        return f"{TournamentService.CACHE_PREFIX}:{tournament_id}"
    
    @staticmethod
    def _invalidate_cache(tournament_id: Optional[int] = None):
        """
        Invalida el caché de torneos.
        
        Args:
            tournament_id: Si se especifica, solo invalida ese torneo.
                          Si es None, invalida todo el caché de torneos.
        """
        if tournament_id:
            cache_key = TournamentService._get_cache_key(tournament_id)
            redis_client.delete(cache_key)
            logger.info(f"🗑️ Caché invalidado para torneo {tournament_id}")
        else:
            # Invalidar todas las listas de torneos
            redis_client.delete_pattern(f"{TournamentService.CACHE_PREFIX}:list:*")
            logger.info(f"🗑️ Caché de listas de torneos invalidado")
    
    @staticmethod
    def create_tournament(db: Session, tournament_data: TournamentCreate) -> Tournament:
        """
        Crea un nuevo torneo.
        
        Args:
            db: Sesión de base de datos
            tournament_data: Datos del torneo a crear
            
        Returns:
            Tournament: Torneo creado
        """
        # Crear instancia del modelo
        tournament = Tournament(
            name=tournament_data.name,
            game=tournament_data.game,
            description=tournament_data.description,
            max_participants=tournament_data.max_participants,
            registration_start=tournament_data.registration_start,
            registration_end=tournament_data.registration_end,
            tournament_start=tournament_data.tournament_start,
            tournament_end=tournament_data.tournament_end,
            status=TournamentStatus.PENDING,
            current_participants=0
        )
        
        # Guardar en la base de datos
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        
        # Invalidar caché de listas
        TournamentService._invalidate_cache()
        
        logger.info(f"✅ Torneo creado: {tournament.name} (ID: {tournament.id})")
        
        return tournament
    
    @staticmethod
    async def create_tournament_async(db: Session, tournament_data: TournamentCreate) -> Tournament:
        """
        Crea un nuevo torneo y publica evento.
        
        Args:
            db: Sesión de base de datos
            tournament_data: Datos del torneo a crear
            
        Returns:
            Tournament: Torneo creado
        """
        # Crear el torneo
        tournament = TournamentService.create_tournament(db, tournament_data)
        
        # Publicar evento
        from app.services.messaging_service import rabbitmq_service
        tournament_dict = tournament.to_dict()
        await rabbitmq_service.publish_tournament_created(tournament_dict)
        
        return tournament
    
    @staticmethod
    def get_tournament_by_id(db: Session, tournament_id: int) -> Tournament:
        """
        Obtiene un torneo por su ID.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo
            
        Returns:
            Tournament: Torneo encontrado
            
        Raises:
            HTTPException: Si no se encuentra el torneo
        """
        # Consultar la base de datos (necesario para operaciones de escritura)
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Torneo con ID {tournament_id} no encontrado"
            )
        
        return tournament
    
    @staticmethod
    def get_tournament_cached(db: Session, tournament_id: int) -> dict:
        """
        Obtiene un torneo por su ID usando caché cuando es posible.
        Retorna un diccionario (no el objeto SQLAlchemy).
        Ideal para endpoints de solo lectura.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo
            
        Returns:
            dict: Datos del torneo
            
        Raises:
            HTTPException: Si no se encuentra el torneo
        """
        # Intentar obtener del caché
        cache_key = TournamentService._get_cache_key(tournament_id)
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            logger.info(f"📦 Torneo {tournament_id} obtenido del caché")
            return cached_data
        
        # Si no está en caché, consultar la base de datos
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Torneo con ID {tournament_id} no encontrado"
            )
        
        # Guardar en caché para futuras consultas
        tournament_dict = tournament.to_dict()
        redis_client.set(cache_key, tournament_dict, ttl=TournamentService.CACHE_TTL)
        logger.info(f"💾 Torneo {tournament_id} guardado en caché")
        
        return tournament_dict
    
    @staticmethod
    def get_tournaments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        game: Optional[str] = None,
        status_filter: Optional[TournamentStatus] = None
    ) -> tuple[List[Tournament], int]:
        """
        Obtiene una lista de torneos con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            game: Filtrar por juego
            status_filter: Filtrar por estado
            
        Returns:
            tuple: (Lista de torneos, Total de registros)
        """
        query = db.query(Tournament)
        
        # Aplicar filtros
        if game:
            query = query.filter(Tournament.game.ilike(f"%{game}%"))
        
        if status_filter:
            query = query.filter(Tournament.status == status_filter)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación y ordenar por fecha de creación
        tournaments = query.order_by(Tournament.created_at.desc()).offset(skip).limit(limit).all()
        
        return tournaments, total
    
    @staticmethod
    def update_tournament(
        db: Session,
        tournament_id: int,
        tournament_data: TournamentUpdate
    ) -> Tournament:
        """
        Actualiza un torneo existente.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo a actualizar
            tournament_data: Datos a actualizar
            
        Returns:
            Tournament: Torneo actualizado
        """
        tournament = TournamentService.get_tournament_by_id(db, tournament_id)
        
        # Actualizar solo los campos que se enviaron
        update_data = tournament_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(tournament, field, value)
        
        db.commit()
        db.refresh(tournament)
        
        # Invalidar caché
        TournamentService._invalidate_cache(tournament_id)
        TournamentService._invalidate_cache()  # También invalida listas
        
        logger.info(f"✏️ Torneo {tournament_id} actualizado")
        
        return tournament
    
    @staticmethod
    async def update_tournament_async(
        db: Session,
        tournament_id: int,
        tournament_data: TournamentUpdate
    ) -> Tournament:
        """
        Actualiza un torneo y publica evento.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo a actualizar
            tournament_data: Datos a actualizar
            
        Returns:
            Tournament: Torneo actualizado
        """
        tournament = TournamentService.update_tournament(db, tournament_id, tournament_data)
        
        # Publicar evento
        from app.services.messaging_service import rabbitmq_service
        tournament_dict = tournament.to_dict()
        await rabbitmq_service.publish_tournament_updated(tournament_dict)
        
        return tournament
    
    @staticmethod
    def delete_tournament(db: Session, tournament_id: int) -> dict:
        """
        Elimina un torneo.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo a eliminar
            
        Returns:
            dict: Mensaje de confirmación
        """
        tournament = TournamentService.get_tournament_by_id(db, tournament_id)
        tournament_name = tournament.name
        
        db.delete(tournament)
        db.commit()
        
        # Invalidar caché
        TournamentService._invalidate_cache(tournament_id)
        TournamentService._invalidate_cache()  # También invalida listas
        
        logger.info(f"🗑️ Torneo {tournament_id} eliminado")
        
        return {"message": f"Torneo '{tournament_name}' eliminado correctamente"}
    
    @staticmethod
    async def delete_tournament_async(db: Session, tournament_id: int) -> dict:
        """
        Elimina un torneo y publica evento.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo a eliminar
            
        Returns:
            dict: Mensaje de confirmación
        """
        tournament = TournamentService.get_tournament_by_id(db, tournament_id)
        tournament_name = tournament.name
        tournament_id_value = tournament.id
        
        result = TournamentService.delete_tournament(db, tournament_id)
        
        # Publicar evento
        from app.services.messaging_service import rabbitmq_service
        await rabbitmq_service.publish_tournament_deleted(tournament_id_value, tournament_name)
        
        return result
    
    @staticmethod
    def change_status(
        db: Session,
        tournament_id: int,
        new_status: TournamentStatus
    ) -> Tournament:
        """
        Cambia el estado de un torneo.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo
            new_status: Nuevo estado
            
        Returns:
            Tournament: Torneo actualizado
        """
        tournament = TournamentService.get_tournament_by_id(db, tournament_id)
        old_status = tournament.status
        tournament.status = new_status
        
        db.commit()
        db.refresh(tournament)
        
        # Invalidar caché
        TournamentService._invalidate_cache(tournament_id)
        TournamentService._invalidate_cache()  # También invalida listas
        
        logger.info(f"🔄 Torneo {tournament_id} cambió de estado: {old_status} → {new_status}")
        
        return tournament
    
    @staticmethod
    async def change_status_async(
        db: Session,
        tournament_id: int,
        new_status: TournamentStatus
    ) -> Tournament:
        """
        Cambia el estado de un torneo y publica evento.
        
        Args:
            db: Sesión de base de datos
            tournament_id: ID del torneo
            new_status: Nuevo estado
            
        Returns:
            Tournament: Torneo actualizado
        """
        tournament = TournamentService.get_tournament_by_id(db, tournament_id)
        old_status = tournament.status.value if tournament.status else None
        
        tournament = TournamentService.change_status(db, tournament_id, new_status)
        
        # Publicar evento
        from app.services.messaging_service import rabbitmq_service
        tournament_dict = tournament.to_dict()
        await rabbitmq_service.publish_tournament_status_changed(
            tournament_id, 
            old_status, 
            new_status.value,
            tournament_dict
        )
        
        return tournament