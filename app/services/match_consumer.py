import aio_pika
import json
import logging
import asyncio
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class MatchConsumer:
    """Consumer para escuchar eventos de matches desde RabbitMQ"""

    def __init__(self):
        """Inicializa el consumer de matches"""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange_name = "tournaments_exchange"
        self.queue_name = "tournaments_service_queue"
        self.consuming = False

    async def connect(self):
        """Establece la conexión con RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.rabbitmq_url,
                timeout=10
            )
            self.channel = await self.connection.channel()

            # Configurar QoS para procesar un mensaje a la vez
            await self.channel.set_qos(prefetch_count=1)

            # Declarar el exchange (debe existir ya)
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Declarar la cola
            self.queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True
            )

            # Bind a los eventos de matches que nos interesan
            await self.queue.bind(
                self.exchange,
                routing_key="match.finished"
            )

            logger.info(f"✅ Consumer conectado a RabbitMQ")
            logger.info(f"👂 Escuchando eventos en cola '{self.queue_name}'")
            logger.info(f"🔗 Binding: match.finished")

        except Exception as e:
            logger.warning(f"⚠️ No se pudo conectar Consumer a RabbitMQ: {e}")
            logger.warning("⚠️ No se procesarán eventos de matches")
            self.connection = None
            self.channel = None

    async def close(self):
        """Cierra la conexión con RabbitMQ"""
        try:
            self.consuming = False
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logger.info("👋 Consumer de matches cerrado")
        except Exception as e:
            logger.error(f"Error al cerrar consumer: {e}")

    def is_connected(self) -> bool:
        """Verifica si está conectado a RabbitMQ"""
        return self.connection is not None and not self.connection.is_closed

    async def process_match_finished(self, message_data: dict):
        """
        Procesa el evento de match finalizado.

        Args:
            message_data: Datos del evento match.finished
        """
        try:
            logger.info(f"🎯 Procesando evento match.finished")

            # Extraer información del match
            match_id = message_data.get("id")
            tournament_id = message_data.get("tournament_id")
            round_number = message_data.get("round")
            match_number = message_data.get("match_number")
            winner_id = message_data.get("winner_id")

            if not all([match_id, tournament_id, round_number, match_number, winner_id]):
                logger.error(f"❌ Datos incompletos en evento match.finished: {message_data}")
                return

            logger.info(f"📊 Match completado: ID={match_id}, Torneo={tournament_id}, Ronda={round_number}, Match#={match_number}, Ganador={winner_id}")

            # Avanzar al ganador a la siguiente ronda
            from app.services.bracket_service import BracketService

            result = await BracketService.advance_winner_to_next_round(
                tournament_id=tournament_id,
                match_id=match_id,
                round_number=round_number,
                match_number=match_number,
                winner_id=winner_id
            )

            logger.info(f"✅ Ganador avanzado a ronda {result['next_round']}, match {result['next_match_number']}")
            logger.info(f"✅ Evento match.finished procesado correctamente")

        except Exception as e:
            logger.error(f"❌ Error al procesar match.finished: {e}")
            raise

    async def on_message(self, message: aio_pika.IncomingMessage):
        """
        Callback que se ejecuta cuando llega un mensaje.

        Args:
            message: Mensaje entrante de RabbitMQ
        """
        async with message.process():
            try:
                # Decodificar el mensaje
                body = json.loads(message.body.decode())

                event_type = body.get("event_type")
                routing_key = body.get("routing_key")
                data = body.get("data", {})

                logger.info(f"📥 Mensaje recibido: {routing_key} ({event_type})")

                # Procesar según el routing key
                if routing_key == "match.finished":
                    await self.process_match_finished(data)
                else:
                    logger.warning(f"⚠️ Routing key no manejado: {routing_key}")

            except json.JSONDecodeError as e:
                logger.error(f"❌ Error al decodificar mensaje JSON: {e}")
            except Exception as e:
                logger.error(f"❌ Error al procesar mensaje: {e}")
                # Re-raise para que el mensaje no sea confirmado y pueda ser reintentado
                raise

    async def start_consuming(self):
        """Inicia el consumo de mensajes"""
        if not self.is_connected():
            logger.warning("⚠️ No conectado a RabbitMQ. No se puede iniciar consumer.")
            return

        try:
            self.consuming = True
            logger.info("🎧 Iniciando consumo de mensajes...")

            # Consumir mensajes de la cola
            await self.queue.consume(self.on_message)

            logger.info("✅ Consumer activo y esperando mensajes")

        except Exception as e:
            logger.error(f"❌ Error al iniciar consumer: {e}")
            self.consuming = False


# Instancia global del consumer
match_consumer = MatchConsumer()
