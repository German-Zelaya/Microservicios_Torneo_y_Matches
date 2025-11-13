import aio_pika
import json
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQService:
    """Servicio para manejar mensajería con RabbitMQ"""
    
    def __init__(self):
        """Inicializa el servicio de RabbitMQ"""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange_name = "tournaments_exchange"
    
    async def connect(self):
        """Establece la conexión con RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.rabbitmq_url,
                timeout=10
            )
            self.channel = await self.connection.channel()
            
            # Declarar el exchange (tipo topic para enrutamiento flexible)
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            logger.info(f"✅ Conectado a RabbitMQ en {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
            logger.info(f"📢 Exchange '{self.exchange_name}' declarado")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo conectar a RabbitMQ: {e}")
            logger.warning("⚠️ Los eventos no se publicarán")
            self.connection = None
            self.channel = None
    
    async def close(self):
        """Cierra la conexión con RabbitMQ"""
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logger.info("👋 Conexión a RabbitMQ cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión a RabbitMQ: {e}")
    
    def is_connected(self) -> bool:
        """Verifica si está conectado a RabbitMQ"""
        return self.connection is not None and not self.connection.is_closed
    
    async def publish_event(
        self,
        routing_key: str,
        event_data: Dict[str, Any],
        event_type: str
    ) -> bool:
        """
        Publica un evento en RabbitMQ.
        
        Args:
            routing_key: Clave de enrutamiento (ej: "tournament.created")
            event_data: Datos del evento
            event_type: Tipo de evento
            
        Returns:
            bool: True si se publicó correctamente
        """
        if not self.is_connected():
            logger.warning(f"⚠️ RabbitMQ no conectado. Evento no publicado: {routing_key}")
            return False
        
        try:
            # Preparar el mensaje
            message_body = {
                "event_type": event_type,
                "routing_key": routing_key,
                "data": event_data
            }
            
            message = aio_pika.Message(
                body=json.dumps(message_body, default=str).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # Mensaje persistente
            )
            
            # Publicar en el exchange
            await self.exchange.publish(
                message,
                routing_key=routing_key
            )
            
            logger.info(f"📤 Evento publicado: {routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al publicar evento {routing_key}: {e}")
            return False
    
    async def publish_tournament_created(self, tournament_data: Dict[str, Any]) -> bool:
        """
        Publica un evento de torneo creado.
        
        Args:
            tournament_data: Datos del torneo creado
            
        Returns:
            bool: True si se publicó correctamente
        """
        return await self.publish_event(
            routing_key="tournament.created",
            event_data=tournament_data,
            event_type="TOURNAMENT_CREATED"
        )
    
    async def publish_tournament_updated(self, tournament_data: Dict[str, Any]) -> bool:
        """
        Publica un evento de torneo actualizado.
        
        Args:
            tournament_data: Datos del torneo actualizado
            
        Returns:
            bool: True si se publicó correctamente
        """
        return await self.publish_event(
            routing_key="tournament.updated",
            event_data=tournament_data,
            event_type="TOURNAMENT_UPDATED"
        )
    
    async def publish_tournament_deleted(self, tournament_id: int, tournament_name: str) -> bool:
        """
        Publica un evento de torneo eliminado.
        
        Args:
            tournament_id: ID del torneo eliminado
            tournament_name: Nombre del torneo eliminado
            
        Returns:
            bool: True si se publicó correctamente
        """
        return await self.publish_event(
            routing_key="tournament.deleted",
            event_data={
                "tournament_id": tournament_id,
                "tournament_name": tournament_name
            },
            event_type="TOURNAMENT_DELETED"
        )
    
    async def publish_tournament_status_changed(
        self,
        tournament_id: int,
        old_status: str,
        new_status: str,
        tournament_data: Dict[str, Any]
    ) -> bool:
        """
        Publica un evento de cambio de estado de torneo.
        
        Args:
            tournament_id: ID del torneo
            old_status: Estado anterior
            new_status: Nuevo estado
            tournament_data: Datos completos del torneo
            
        Returns:
            bool: True si se publicó correctamente
        """
        return await self.publish_event(
            routing_key=f"tournament.status.{new_status}",
            event_data={
                **tournament_data,
                "old_status": old_status,
                "new_status": new_status
            },
            event_type="TOURNAMENT_STATUS_CHANGED"
        )


# Instancia global del servicio de RabbitMQ
rabbitmq_service = RabbitMQService()