import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Cliente de Redis para manejo de caché"""
    
    def __init__(self):
        """Inicializa la conexión a Redis"""
        self.client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Establece la conexión con Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,  # Decodifica automáticamente a strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Verificar conexión
            self.client.ping()
            logger.info(f"✅ Conectado a Redis en {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ No se pudo conectar a Redis: {e}")
            logger.warning("⚠️ La aplicación funcionará sin caché")
            self.client = None
        except Exception as e:
            logger.error(f"❌ Error inesperado al conectar a Redis: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Verifica si Redis está conectado"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Clave a buscar
            
        Returns:
            Valor deserializado o None si no existe
        """
        if not self.is_connected():
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error al obtener de Redis: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Guarda un valor en el caché.
        
        Args:
            key: Clave
            value: Valor a guardar (será serializado a JSON)
            ttl: Tiempo de vida en segundos (default: 5 minutos)
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        if not self.is_connected():
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error al guardar en Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Elimina una clave del caché.
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó, False en caso contrario
        """
        if not self.is_connected():
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error al eliminar de Redis: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Elimina todas las claves que coinciden con un patrón.
        
        Args:
            pattern: Patrón de búsqueda (ej: "tournament:*")
            
        Returns:
            Número de claves eliminadas
        """
        if not self.is_connected():
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error al eliminar patrón de Redis: {e}")
            return 0
    
    def flush_all(self) -> bool:
        """
        Elimina todas las claves del caché.
        
        Returns:
            True si se limpió correctamente
        """
        if not self.is_connected():
            return False
        
        try:
            self.client.flushdb()
            logger.info("🗑️ Caché de Redis limpiado")
            return True
        except Exception as e:
            logger.error(f"Error al limpiar Redis: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a Redis"""
        if self.client:
            try:
                self.client.close()
                logger.info("👋 Conexión a Redis cerrada")
            except Exception as e:
                logger.error(f"Error al cerrar conexión a Redis: {e}")


# Instancia global del cliente Redis
redis_client = RedisClient()