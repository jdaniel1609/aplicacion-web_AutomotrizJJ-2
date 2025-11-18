import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_database, seed_initial_data
from app.routes import auth, venta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando aplicación...")
    logger.info(f"🔧 Modo de base de datos: {settings.DB_TYPE}")
    
    try:
        # Inicializar base de datos
        init_database()
        
        # Cargar datos iniciales si es necesario
        seed_initial_data()
        
        logger.info("✅ Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al iniciar la aplicación: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Automotriz JJ API",
    description="API para gestión de ventas de vehículos",
    version="2.0.0",
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

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(venta.router, prefix="/api", tags=["Ventas"])


@app.get("/")
async def root():
    """
    Endpoint raíz de la API
    """
    return {
        "message": "Bienvenido a Automotriz JJ API",
        "version": "2.0.0",
        "db_type": settings.DB_TYPE,
        "endpoints": {
            "auth": "/auth",
            "ventas": "/api/ventas",
            "vehiculos": "/api/vehiculos",
            "vendedores": "/api/vendedores",
            "tiendas": "/api/tiendas",
            "clientes": "/api/clientes",
            "statistics": "/api/statistics"
        }
    }


@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la aplicación
    """
    return {
        "status": "healthy",
        "db_type": settings.DB_TYPE,
        "version": "2.0.0"
    }