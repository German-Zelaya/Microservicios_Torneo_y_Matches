from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database.session import init_db
from app.api.v1 import tournaments

# Configurar logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la app.
    """
    # Startup
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Inicializar base de datos
        logger.info("📊 Conectando a PostgreSQL...")
        init_db()
        logger.info("✅ Base de datos conectada")
    except Exception as e:
        logger.error(f"❌ Error al conectar a la base de datos: {e}")
        raise
    
    # Redis se conecta automáticamente al importar redis_client
    from app.cache.redis_client import redis_client
    if redis_client.is_connected():
        logger.info("✅ Redis conectado y listo")
    else:
        logger.warning("⚠️ Redis no disponible - continuando sin caché")
    
    # Conectar a RabbitMQ (Producer)
    from app.services.messaging_service import rabbitmq_service
    await rabbitmq_service.connect()
    if rabbitmq_service.is_connected():
        logger.info("✅ RabbitMQ Producer conectado y listo")
    else:
        logger.warning("⚠️ RabbitMQ Producer no disponible - los eventos no se publicarán")

    # Conectar a RabbitMQ (Consumer)
    from app.services.match_consumer import match_consumer
    await match_consumer.connect()
    if match_consumer.is_connected():
        logger.info("✅ RabbitMQ Consumer conectado")
        # Iniciar consumo de mensajes en background
        import asyncio
        asyncio.create_task(match_consumer.start_consuming())
        logger.info("🎧 Consumer de matches iniciado en background")
    else:
        logger.warning("⚠️ RabbitMQ Consumer no disponible - no se procesarán eventos de matches")

    yield

    # Shutdown
    logger.info("👋 Cerrando aplicación...")

    # Cerrar conexión a Redis
    from app.cache.redis_client import redis_client
    redis_client.close()

    # Cerrar Consumer de RabbitMQ
    from app.services.match_consumer import match_consumer
    await match_consumer.close()

    # Cerrar Producer de RabbitMQ
    from app.services.messaging_service import rabbitmq_service
    await rabbitmq_service.close()


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservicio para gestión de torneos de eSports",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(tournaments.router, prefix="/api/v1")


# ============= ENDPOINTS =============

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifica que el servicio esté funcionando.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health/db")
async def database_health():
    """
    Verifica la conexión a la base de datos.
    """
    from app.database.session import engine
    from sqlalchemy import text
    
    try:
        # Intentar conectar y ejecutar query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "connected": False,
            "error": str(e)
        }


@app.get("/health/redis")
async def redis_health():
    """
    Verifica la conexión a Redis.
    """
    from app.cache.redis_client import redis_client
    
    is_connected = redis_client.is_connected()
    
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "service": "Redis",
        "connected": is_connected,
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT
    }


@app.get("/health/rabbitmq")
async def rabbitmq_health():
    """
    Verifica la conexión a RabbitMQ.
    """
    from app.services.messaging_service import rabbitmq_service
    
    is_connected = rabbitmq_service.is_connected()
    
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "service": "RabbitMQ",
        "connected": is_connected,
        "host": settings.RABBITMQ_HOST,
        "port": settings.RABBITMQ_PORT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )