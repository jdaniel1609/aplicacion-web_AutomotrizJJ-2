from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información de la aplicación
    APP_NAME: str = "Automotriz JJ API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./automotriz_jj.db"
    
    # Usuarios por defecto
    DEFAULT_USERNAME: str = "admin"
    DEFAULT_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins(self) -> List[str]:
        """Convierte string de origenes en lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Instancia global de configuración
settings = Settings()