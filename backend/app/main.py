import logging
import os
import time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, venta

# Importar funciones de database para inicialización
try:
    from app.database import init_database, seed_initial_data
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logging.warning("No se pudieron importar funciones de database")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aplicacion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para el sistema de gestión de Automotriz JJ",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Log de entrada
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    logger.info(f"Client IP: {request.client.host}")
    
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Log de salida
    logger.info(f"Completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
    
    return response

# Incluir routers
app.include_router(auth.router)
app.include_router(venta.router)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Bienvenido a la API de Automotriz JJ",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    logger.info("Health check accessed")
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ============================================
# FUNCIONES DE INICIALIZACIÓN DE BASE DE DATOS
# ============================================

def wait_for_database(max_retries=10, retry_delay=5):
    """
    Espera a que la base de datos esté disponible
    
    Args:
        max_retries: Número máximo de intentos
        retry_delay: Segundos entre intentos
        
    Returns:
        bool: True si la BD está disponible, False si no
    """
    if not DATABASE_AVAILABLE:
        logger.error("Funciones de database no disponibles")
        return False
    
    # Solo esperar si estamos usando Azure SQL
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    if db_type != 'azure':
        logger.info("Usando SQLite, no es necesario esperar")
        return True
    
    import pyodbc
    
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    driver = os.getenv('AZURE_SQL_DRIVER', '{ODBC Driver 18 for SQL Server}')
    
    connection_string = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=30;'
    )
    
    logger.info("🔄 Esperando a que Azure SQL Database esté disponible...")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Intento {attempt}/{max_retries} de conexión a {server}/{database}")
            conn = pyodbc.connect(connection_string)
            conn.close()
            logger.info("✅ Base de datos disponible!")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Intento {attempt} falló: {e}")
            if attempt < max_retries:
                logger.info(f"Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ No se pudo conectar a la base de datos después de múltiples intentos")
                return False
    
    return False


def initialize_database():
    """
    Inicializa la base de datos: crea tablas e inserta datos iniciales
    
    Returns:
        bool: True si la inicialización fue exitosa, False si no
    """
    if not DATABASE_AVAILABLE:
        logger.error("Funciones de database no disponibles")
        return False
    
    try:
        logger.info("📊 Inicializando base de datos...")
        
        # Crear tablas
        logger.info("🔨 Creando tablas si no existen...")
        init_database()
        logger.info("✅ Tablas verificadas/creadas")
        
        # Insertar datos iniciales
        logger.info("📝 Verificando/insertando datos iniciales...")
        seed_initial_data()
        logger.info("✅ Datos iniciales verificados/insertados")
        
        logger.info("✅ Inicialización de base de datos completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización de BD: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


# ============================================
# EVENTOS DE INICIO Y CIERRE
# ============================================

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando la aplicación inicia"""
    logger.info("=" * 70)
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 70)
    
    # Verificar tipo de base de datos
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    logger.info(f"📊 Tipo de base de datos: {db_type.upper()}")
    
    # Inicializar base de datos
    try:
        if DATABASE_AVAILABLE:
            # Esperar a que la base de datos esté disponible (solo para Azure SQL)
            if db_type == 'azure':
                if not wait_for_database():
                    logger.error("❌ Base de datos no disponible, pero continuando...")
                    logger.error("⚠️ La aplicación puede no funcionar correctamente")
            
            # Inicializar base de datos
            if initialize_database():
                logger.info("✅ Base de datos lista")
            else:
                logger.error("❌ Error al inicializar base de datos")
                logger.error("⚠️ La aplicación puede no funcionar correctamente")
        else:
            logger.warning("⚠️ Funciones de database no disponibles, omitiendo inicialización")
    except Exception as e:
        logger.error(f"❌ Error crítico al inicializar base de datos: {e}")
        logger.error("⚠️ La aplicación continuará pero puede no funcionar correctamente")
    
    logger.info("")
    logger.info(f"📝 Documentación disponible en: /docs")
    logger.info(f"🔐 Usuario de prueba: {settings.DEFAULT_USERNAME}")
    logger.info(f"🔑 Contraseña de prueba: {settings.DEFAULT_PASSWORD}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Se ejecuta cuando la aplicación se cierra"""
    logger.info("=" * 70)
    logger.info(f"👋 Cerrando {settings.APP_NAME}")
    logger.info("=" * 70)