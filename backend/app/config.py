from pydantic_settings import BaseSettings
from typing import List, Literal
import os


class Settings(BaseSettings):
    """Configuración de la aplicación con soporte para Azure SQL Database"""
    
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
    
    # Tipo de base de datos: "sqlite" o "azure"
    DB_TYPE: Literal["sqlite", "azure"] = "sqlite"
    
    # SQLite (configuración por defecto)
    DATABASE_URL: str = "sqlite:///./automotriz_jj.db"
    
    # Azure SQL Database (solo se usa si DB_TYPE = "azure")
    AZURE_SQL_SERVER: str = ""
    AZURE_SQL_DATABASE: str = ""
    AZURE_SQL_USERNAME: str = ""
    AZURE_SQL_PASSWORD: str = ""
    AZURE_SQL_DRIVER: str = "{ODBC Driver 18 for SQL Server}"
    AZURE_SQL_PORT: int = 1433
    
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
    
    @property
    def is_azure_db(self) -> bool:
        """Verifica si se está usando Azure SQL Database"""
        return self.DB_TYPE.lower() == "azure"
    
    @property
    def azure_connection_string(self) -> str:
        """Genera la cadena de conexión para Azure SQL Database"""
        if not self.is_azure_db:
            raise ValueError("DB_TYPE debe ser 'azure' para obtener la cadena de conexión de Azure")
        
        return (
            f"DRIVER={self.AZURE_SQL_DRIVER};"
            f"SERVER={self.AZURE_SQL_SERVER},{self.AZURE_SQL_PORT};"
            f"DATABASE={self.AZURE_SQL_DATABASE};"
            f"UID={self.AZURE_SQL_USERNAME};"
            f"PWD={self.AZURE_SQL_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
    
    def validate_azure_config(self) -> bool:
        """Valida que todas las configuraciones de Azure estén presentes"""
        if not self.is_azure_db:
            return True
        
        required_fields = [
            self.AZURE_SQL_SERVER,
            self.AZURE_SQL_DATABASE,
            self.AZURE_SQL_USERNAME,
            self.AZURE_SQL_PASSWORD
        ]
        
        return all(field for field in required_fields)


# Instancia global de configuración
settings = Settings()

# Validar configuración al importar
if settings.is_azure_db and not settings.validate_azure_config():
    raise ValueError(
        "Configuración de Azure SQL Database incompleta. "
        "Verifica que todas las variables AZURE_SQL_* estén definidas en el archivo .env"
    )