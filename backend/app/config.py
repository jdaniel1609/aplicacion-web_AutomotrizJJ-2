from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno
    """
    
    # Configuración de Base de Datos
    DB_TYPE: str = "sqlite"  # sqlite o azure
    
    # Azure SQL Database (solo si DB_TYPE=azure)
    AZURE_SQL_SERVER: str = ""
    AZURE_SQL_DATABASE: str = "automotrizjj"
    AZURE_SQL_USER: str = ""
    AZURE_SQL_PASSWORD: str = ""
    AZURE_SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    
    # JWT
    SECRET_KEY: str = "tu-clave-secreta-super-segura-cambiame-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    @property
    def azure_connection_string(self) -> str:
        """
        Genera la cadena de conexión para Azure SQL Database
        """
        if self.DB_TYPE.lower() != "azure":
            return ""
        
        return (
            f"DRIVER={{{self.AZURE_SQL_DRIVER}}};"
            f"SERVER={self.AZURE_SQL_SERVER};"
            f"DATABASE={self.AZURE_SQL_DATABASE};"
            f"UID={self.AZURE_SQL_USER};"
            f"PWD={self.AZURE_SQL_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()