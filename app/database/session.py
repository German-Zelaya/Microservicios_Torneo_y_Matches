from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Muestra las queries SQL en consola
    pool_pre_ping=True,     # Verifica conexiones antes de usarlas
    pool_size=5,            # Número de conexiones en el pool
    max_overflow=10         # Conexiones adicionales si el pool está lleno
)

# Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener una sesión de base de datos.
    Se usa en los endpoints de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Se llama al iniciar la aplicación.
    """
    Base.metadata.create_all(bind=engine)