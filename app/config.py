from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""
    
    # Application
    APP_NAME: str = "Tournaments Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8001
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = True
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # External Services
    AUTH_SERVICE_URL: str = "http://localhost:3000"
    TEAMS_SERVICE_URL: str = "http://localhost:3002"
    
    @property
    def rabbitmq_url(self) -> str:
        """Construye la URL de RabbitMQ"""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()