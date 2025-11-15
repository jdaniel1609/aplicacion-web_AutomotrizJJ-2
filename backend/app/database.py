import sqlite3
import pyodbc
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)

# Constantes
SQLITE_DATABASE_PATH = "automotriz_jj.db"


class DatabaseManager:
    """Gestor de base de datos que soporta SQLite y Azure SQL Database"""
    
    def __init__(self):
        self.db_type = settings.DB_TYPE.lower()
        logger.info(f"📊 Tipo de base de datos: {self.db_type.upper()}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener una conexión a la base de datos"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(SQLITE_DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
            finally:
                conn.close()
        else:  # azure
            conn = pyodbc.connect(settings.azure_connection_string)
            try:
                yield conn
            finally:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None):
        """
        Ejecuta una query y retorna resultados
        
        Args:
            query: SQL query a ejecutar
            params: Parámetros para la query
            fetch: 'one', 'all', o None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch == "one":
                result = cursor.fetchone()
                return dict(result) if result and self.db_type == "sqlite" else result
            elif fetch == "all":
                results = cursor.fetchall()
                if self.db_type == "sqlite":
                    return [dict(row) for row in results]
                return results
            else:
                conn.commit()
                return cursor.lastrowid if self.db_type == "sqlite" else cursor.rowcount
    
    def _adapt_query_for_azure(self, sqlite_query: str) -> str:
        """Convierte una query de SQLite a SQL Server"""
        query = sqlite_query
        
        # Reemplazar AUTOINCREMENT por IDENTITY
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", 
                            "INT PRIMARY KEY IDENTITY(1,1)")
        
        # Reemplazar tipos de datos
        query = query.replace("TEXT", "NVARCHAR(255)")
        query = query.replace("REAL", "DECIMAL(18,2)")
        query = query.replace("INTEGER", "INT")
        query = query.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", 
                            "DATETIME DEFAULT GETDATE()")
        
        # Reemplazar PRAGMA
        if "PRAGMA" in query:
            return ""  # Las pragmas no existen en SQL Server
        
        # Adaptar constraints de longitud
        query = query.replace("length(", "LEN(")
        
        # Adaptar UNIQUE en columnas
        if "UNIQUE NOT NULL" in query:
            query = query.replace("UNIQUE NOT NULL", "NOT NULL UNIQUE")
        
        return query


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


def get_db_connection():
    """
    Función de compatibilidad para código existente.
    Retorna una conexión a la base de datos apropiada.
    """
    if db_manager.db_type == "sqlite":
        conn = sqlite3.connect(SQLITE_DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    else:
        return pyodbc.connect(settings.azure_connection_string)


def wait_for_azure_db(max_retries: int = 30, retry_delay: int = 2) -> bool:
    """
    Espera a que Azure SQL Database esté disponible
    
    Args:
        max_retries: Número máximo de intentos
        retry_delay: Segundos entre intentos
        
    Returns:
        True si la base de datos está disponible, False en caso contrario
    """
    if db_manager.db_type != "azure":
        return True
    
    logger.info("🔄 Esperando a que Azure SQL Database esté disponible...")
    
    for attempt in range(1, max_retries + 1):
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                logger.info("✅ Base de datos disponible!")
                return True
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Intento {attempt}/{max_retries} fallido: {str(e)[:100]}")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ No se pudo conectar después de {max_retries} intentos")
                return False
    
    return False


def init_database():
    """
    Inicializa la base de datos y crea las tablas con sus relaciones.
    Compatible con SQLite y Azure SQL Database.
    
    ESTRUCTURA DE RELACIONES:
    ========================
    vendedores (Tabla Principal)
    ├── id (PRIMARY KEY)
    └── Relación: registro_venta.vendedor_id → vendedores.id
    
    autos_disponibles (Tabla Principal)
    ├── id (PRIMARY KEY)
    └── Relación: registro_venta.auto_id → autos_disponibles.id
    
    registro_venta (Tabla Dependiente)
    ├── id (PRIMARY KEY)
    ├── vendedor_id (FOREIGN KEY → vendedores.id)
    └── auto_id (FOREIGN KEY → autos_disponibles.id)
    """
    
    # Esperar a que Azure esté disponible
    if db_manager.db_type == "azure":
        if not wait_for_azure_db():
            raise Exception("No se pudo conectar a Azure SQL Database")
    
    try:
        logger.info("📊 Inicializando base de datos...")
        
        if db_manager.db_type == "sqlite":
            _init_sqlite_database()
        else:
            _init_azure_database()
        
        logger.info("✅ Base de datos inicializada correctamente con todas las relaciones")
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {e}")
        raise


def _init_sqlite_database():
    """Inicializa la base de datos SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabla vendedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'vendedor',
                codigo_vendedor TEXT UNIQUE NOT NULL,
                sucursal_provincia TEXT NOT NULL,
                sucursal_distrito TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT chk_username_length CHECK(length(username) >= 3),
                CONSTRAINT chk_codigo_vendedor_format CHECK(codigo_vendedor LIKE 'VEN%')
            )
        ''')
        
        # Índices para vendedores
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendedores_username ON vendedores(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendedores_codigo ON vendedores(codigo_vendedor)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendedores_provincia ON vendedores(sucursal_provincia)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendedores_distrito ON vendedores(sucursal_distrito)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendedores_active ON vendedores(is_active)')
        
        logger.info("✅ Tabla 'vendedores' creada con PRIMARY KEY: id")
        
        # Tabla autos_disponibles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autos_disponibles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                anio INTEGER NOT NULL,
                precio_referencial REAL,
                stock INTEGER DEFAULT 25,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT chk_anio_valido CHECK(anio >= 2020 AND anio <= 2030),
                CONSTRAINT chk_precio_positivo CHECK(precio_referencial > 0),
                CONSTRAINT chk_stock_positivo CHECK(stock >= 0),
                CONSTRAINT uq_auto UNIQUE(marca, modelo, anio)
            )
        ''')
        
        # Índices para autos_disponibles
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_autos_marca ON autos_disponibles(marca)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_autos_modelo ON autos_disponibles(modelo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_autos_anio ON autos_disponibles(anio)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_autos_active ON autos_disponibles(is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_autos_marca_modelo ON autos_disponibles(marca, modelo)')
        
        logger.info("✅ Tabla 'autos_disponibles' creada con PRIMARY KEY: id")
        
        # Tabla registro_venta
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                vendedor_id INTEGER NOT NULL,
                auto_id INTEGER NOT NULL,
                tipo_compra TEXT NOT NULL CHECK(tipo_compra IN ('Cash', 'Crédito')),
                monto_fisco TEXT NOT NULL,
                nombre_comprador TEXT NOT NULL,
                dni_comprador TEXT NOT NULL,
                contacto_comprador TEXT NOT NULL,
                sucursal_provincia TEXT NOT NULL,
                sucursal_distrito TEXT NOT NULL,
                nombre_vendedor TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_venta_vendedor 
                    FOREIGN KEY (vendedor_id) 
                    REFERENCES vendedores(id) 
                    ON DELETE CASCADE 
                    ON UPDATE CASCADE,
                    
                CONSTRAINT fk_venta_auto 
                    FOREIGN KEY (auto_id) 
                    REFERENCES autos_disponibles(id) 
                    ON DELETE CASCADE 
                    ON UPDATE CASCADE,
                
                CONSTRAINT chk_dni_length CHECK(length(dni_comprador) = 8),
                CONSTRAINT chk_monto_not_empty CHECK(length(monto_fisco) > 0)
            )
        ''')
        
        # Índices para registro_venta
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_fecha ON registro_venta(fecha_venta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_vendedor ON registro_venta(vendedor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_auto ON registro_venta(auto_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_tipo_compra ON registro_venta(tipo_compra)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_dni ON registro_venta(dni_comprador)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_provincia ON registro_venta(sucursal_provincia)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_distrito ON registro_venta(sucursal_distrito)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venta_fecha_vendedor ON registro_venta(fecha_venta, vendedor_id)')
        
        logger.info("✅ Tabla 'registro_venta' creada con FOREIGN KEYS")
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error en SQLite: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_azure_database():
    """Inicializa la base de datos Azure SQL Database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si las tablas ya existen
        cursor.execute("""
            SELECT COUNT(*) as cnt 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'vendedores'
        """)
        
        if cursor.fetchone()[0] > 0:
            logger.info("Las tablas ya existen en Azure SQL Database")
            return
        
        # Tabla vendedores
        cursor.execute('''
            CREATE TABLE vendedores (
                id INT PRIMARY KEY IDENTITY(1,1),
                username NVARCHAR(255) UNIQUE NOT NULL,
                password_hash NVARCHAR(255) NOT NULL,
                full_name NVARCHAR(255) NOT NULL,
                email NVARCHAR(255),
                role NVARCHAR(50) DEFAULT 'vendedor',
                codigo_vendedor NVARCHAR(50) UNIQUE NOT NULL,
                sucursal_provincia NVARCHAR(100) NOT NULL,
                sucursal_distrito NVARCHAR(100) NOT NULL,
                is_active INT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE(),
                
                CONSTRAINT chk_username_length CHECK(LEN(username) >= 3),
                CONSTRAINT chk_codigo_vendedor_format CHECK(codigo_vendedor LIKE 'VEN%')
            )
        ''')
        
        # Índices para vendedores
        cursor.execute('CREATE INDEX idx_vendedores_username ON vendedores(username)')
        cursor.execute('CREATE INDEX idx_vendedores_codigo ON vendedores(codigo_vendedor)')
        cursor.execute('CREATE INDEX idx_vendedores_provincia ON vendedores(sucursal_provincia)')
        cursor.execute('CREATE INDEX idx_vendedores_distrito ON vendedores(sucursal_distrito)')
        cursor.execute('CREATE INDEX idx_vendedores_active ON vendedores(is_active)')
        
        logger.info("✅ Tabla 'vendedores' creada con PRIMARY KEY: id")
        
        # Tabla autos_disponibles
        cursor.execute('''
            CREATE TABLE autos_disponibles (
                id INT PRIMARY KEY IDENTITY(1,1),
                marca NVARCHAR(100) NOT NULL,
                modelo NVARCHAR(100) NOT NULL,
                anio INT NOT NULL,
                precio_referencial DECIMAL(18,2),
                stock INT DEFAULT 25,
                is_active INT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE(),
                
                CONSTRAINT chk_anio_valido CHECK(anio >= 2020 AND anio <= 2030),
                CONSTRAINT chk_precio_positivo CHECK(precio_referencial > 0),
                CONSTRAINT chk_stock_positivo CHECK(stock >= 0),
                CONSTRAINT uq_auto UNIQUE(marca, modelo, anio)
            )
        ''')
        
        # Índices para autos_disponibles
        cursor.execute('CREATE INDEX idx_autos_marca ON autos_disponibles(marca)')
        cursor.execute('CREATE INDEX idx_autos_modelo ON autos_disponibles(modelo)')
        cursor.execute('CREATE INDEX idx_autos_anio ON autos_disponibles(anio)')
        cursor.execute('CREATE INDEX idx_autos_active ON autos_disponibles(is_active)')
        cursor.execute('CREATE INDEX idx_autos_marca_modelo ON autos_disponibles(marca, modelo)')
        
        logger.info("✅ Tabla 'autos_disponibles' creada con PRIMARY KEY: id")
        
        # Tabla registro_venta
        cursor.execute('''
            CREATE TABLE registro_venta (
                id INT PRIMARY KEY IDENTITY(1,1),
                fecha_venta DATETIME DEFAULT GETDATE(),
                vendedor_id INT NOT NULL,
                auto_id INT NOT NULL,
                tipo_compra NVARCHAR(20) NOT NULL CHECK(tipo_compra IN ('Cash', 'Crédito')),
                monto_fisco NVARCHAR(50) NOT NULL,
                nombre_comprador NVARCHAR(255) NOT NULL,
                dni_comprador NVARCHAR(8) NOT NULL,
                contacto_comprador NVARCHAR(20) NOT NULL,
                sucursal_provincia NVARCHAR(100) NOT NULL,
                sucursal_distrito NVARCHAR(100) NOT NULL,
                nombre_vendedor NVARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT GETDATE(),
                
                CONSTRAINT fk_venta_vendedor 
                    FOREIGN KEY (vendedor_id) 
                    REFERENCES vendedores(id) 
                    ON DELETE CASCADE 
                    ON UPDATE CASCADE,
                    
                CONSTRAINT fk_venta_auto 
                    FOREIGN KEY (auto_id) 
                    REFERENCES autos_disponibles(id) 
                    ON DELETE CASCADE 
                    ON UPDATE CASCADE,
                
                CONSTRAINT chk_dni_length CHECK(LEN(dni_comprador) = 8),
                CONSTRAINT chk_monto_not_empty CHECK(LEN(monto_fisco) > 0)
            )
        ''')
        
        # Índices para registro_venta
        cursor.execute('CREATE INDEX idx_venta_fecha ON registro_venta(fecha_venta)')
        cursor.execute('CREATE INDEX idx_venta_vendedor ON registro_venta(vendedor_id)')
        cursor.execute('CREATE INDEX idx_venta_auto ON registro_venta(auto_id)')
        cursor.execute('CREATE INDEX idx_venta_tipo_compra ON registro_venta(tipo_compra)')
        cursor.execute('CREATE INDEX idx_venta_dni ON registro_venta(dni_comprador)')
        cursor.execute('CREATE INDEX idx_venta_provincia ON registro_venta(sucursal_provincia)')
        cursor.execute('CREATE INDEX idx_venta_distrito ON registro_venta(sucursal_distrito)')
        
        logger.info("✅ Tabla 'registro_venta' creada con FOREIGN KEYS")
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error en Azure SQL: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def seed_initial_data():
    """Inserta datos iniciales en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM vendedores")
        result = cursor.fetchone()
        count = result[0] if db_manager.db_type == "azure" else result[0]
        
        if count > 0:
            logger.info("Los datos iniciales ya existen, omitiendo seed...")
            return
        
        import hashlib
        
        logger.info("📝 Insertando datos iniciales...")
        
        # PASO 1: Insertar VENDEDORES
        vendedores = [
            ('cmendoza', 'carlos2020', 'Carlos Mendoza', 'cmendoza@automotrizjj.com', 'vendedor', 'VEN001', 'LIMA', 'Miraflores'),
            ('svargas', 'sofia2020', 'Sofía Vargas', 'svargas@automotrizjj.com', 'vendedor', 'VEN002', 'LIMA', 'Miraflores'),
            ('mrojas', 'miguel2020', 'Miguel Rojas', 'mrojas@automotrizjj.com', 'vendedor', 'VEN003', 'LIMA', 'San Isidro'),
            ('ldiaz', 'laura2020', 'Laura Díaz', 'ldiaz@automotrizjj.com', 'vendedor', 'VEN004', 'LIMA', 'San Isidro'),
            ('dcruz', 'diego2020', 'Diego Cruz', 'dcruz@automotrizjj.com', 'vendedor', 'VEN005', 'LIMA', 'Surco'),
            ('alopez', 'andrea2020', 'Andrea López', 'alopez@automotrizjj.com', 'vendedor', 'VEN006', 'LIMA', 'Surco'),
            ('rsilva', 'roberto2020', 'Roberto Silva', 'rsilva@automotrizjj.com', 'vendedor', 'VEN007', 'LIMA', 'La Molina'),
            ('ptorres', 'patricia2020', 'Patricia Torres', 'ptorres@automotrizjj.com', 'vendedor', 'VEN008', 'LIMA', 'La Molina'),
            ('fcampos', 'fernando2020', 'Fernando Campos', 'fcampos@automotrizjj.com', 'vendedor', 'VEN009', 'PIURA', 'Piura Centro'),
            ('vmorales', 'valentina2020', 'Valentina Morales', 'vmorales@automotrizjj.com', 'vendedor', 'VEN010', 'PIURA', 'Piura Centro'),
            ('mquispe', 'marco2020', 'Marco Quispe', 'mquispe@automotrizjj.com', 'vendedor', 'VEN011', 'AYACUCHO', 'Ayacucho Centro'),
            ('chuaman', 'carmen2020', 'Carmen Huamán', 'chuaman@automotrizjj.com', 'vendedor', 'VEN012', 'AYACUCHO', 'Ayacucho Centro'),
        ]
        
        for username, password, full_name, email, role, codigo, provincia, distrito in vendedores:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if db_manager.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO vendedores (username, password_hash, full_name, email, role, codigo_vendedor, sucursal_provincia, sucursal_distrito)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, full_name, email, role, codigo, provincia, distrito))
            else:  # azure
                cursor.execute('''
                    INSERT INTO vendedores (username, password_hash, full_name, email, role, codigo_vendedor, sucursal_provincia, sucursal_distrito)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', username, password_hash, full_name, email, role, codigo, provincia, distrito)
        
        logger.info(f"✅ Insertados {len(vendedores)} vendedores")
        
        # PASO 2: Insertar AUTOS
        autos_base = [
            ('Toyota', 'Corolla', 85000.00),
            ('Toyota', 'Yaris', 65000.00),
            ('Toyota', 'RAV4', 125000.00),
            ('Honda', 'Civic', 90000.00),
            ('Honda', 'CR-V', 130000.00),
            ('Honda', 'Accord', 110000.00),
            ('Nissan', 'Sentra', 75000.00),
            ('Nissan', 'Kicks', 80000.00),
            ('Nissan', 'X-Trail', 120000.00),
            ('Hyundai', 'Elantra', 78000.00),
            ('Hyundai', 'Tucson', 115000.00),
            ('Hyundai', 'Accent', 62000.00),
            ('Mazda', '3', 88000.00),
            ('Mazda', 'CX-5', 128000.00),
            ('Mazda', '2', 68000.00),
            ('Kia', 'Forte', 76000.00),
            ('Kia', 'Sportage', 122000.00),
            ('Kia', 'Rio', 64000.00),
            ('Chevrolet', 'Cruze', 82000.00),
            ('Chevrolet', 'Tracker', 95000.00),
            ('Ford', 'Focus', 79000.00),
            ('Ford', 'Escape', 118000.00),
            ('BMW', 'Serie 3', 180000.00),
            ('BMW', 'X3', 220000.00)
        ]
        
        # Autos 2024
        for marca, modelo, precio in autos_base:
            if db_manager.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                    VALUES (?, ?, ?, ?, ?)
                ''', (marca, modelo, 2024, precio, 25))
            else:
                cursor.execute('''
                    INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                    VALUES (?, ?, ?, ?, ?)
                ''', marca, modelo, 2024, precio, 25)
        
        # Autos 2025
        for marca, modelo, precio_2024 in autos_base:
            incremento = random.randrange(25000, 75001, 10)
            precio_2025 = precio_2024 + incremento
            
            if db_manager.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                    VALUES (?, ?, ?, ?, ?)
                ''', (marca, modelo, 2025, precio_2025, 25))
            else:
                cursor.execute('''
                    INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                    VALUES (?, ?, ?, ?, ?)
                ''', marca, modelo, 2025, precio_2025, 25)
        
        logger.info(f"✅ Insertados {len(autos_base) * 2} autos (2024 y 2025)")
        conn.commit()
        
        # PASO 3: Insertar VENTAS
        cursor.execute('SELECT id FROM vendedores')
        vendedor_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT id, marca, modelo, anio, precio_referencial FROM autos_disponibles')
        autos = cursor.fetchall()
        
        tipos_compra = ['Cash', 'Crédito']
        nombres = ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Luis Rodríguez', 
                   'Carmen Silva', 'José Torres', 'Elena Flores', 'Pedro Ramírez', 'Isabel Castro']
        
        ventas_por_auto = {}
        for auto in autos:
            auto_id = auto[0]
            num_ventas = random.randint(5, 20)
            ventas_por_auto[auto_id] = (num_ventas, auto)
        
        total_ventas = 0
        fecha_inicio = datetime.now() - timedelta(days=180)
        
        for auto_id, (num_ventas, auto_info) in ventas_por_auto.items():
            for _ in range(num_ventas):
                if total_ventas >= 432:
                    break
                
                vendedor_id = random.choice(vendedor_ids)
                
                cursor.execute('''
                    SELECT full_name, sucursal_provincia, sucursal_distrito 
                    FROM vendedores WHERE id = ?
                ''', (vendedor_id,))
                vendedor_data = cursor.fetchone()
                
                tipo_compra = random.choice(tipos_compra)
                nombre_comprador = random.choice(nombres)
                dni_comprador = str(random.randint(10000000, 99999999))
                contacto_comprador = f"9{random.randint(10000000, 99999999)}"
                
                precio_base = auto_info[4]
                variacion = random.uniform(0.9, 1.1)
                monto = int(float(precio_base) * variacion)
                monto_texto = f"S/. {monto:,.2f}"
                
                dias_atras = random.randint(0, 180)
                fecha_venta = fecha_inicio + timedelta(days=dias_atras)
                
                if db_manager.db_type == "sqlite":
                    cursor.execute('''
                        INSERT INTO registro_venta (
                            fecha_venta, vendedor_id, auto_id, tipo_compra, monto_fisco,
                            nombre_comprador, dni_comprador, contacto_comprador,
                            sucursal_provincia, sucursal_distrito, nombre_vendedor
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fecha_venta, vendedor_id, auto_id, tipo_compra, monto_texto,
                        nombre_comprador, dni_comprador, contacto_comprador,
                        vendedor_data[1], vendedor_data[2], vendedor_data[0]
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO registro_venta (
                            fecha_venta, vendedor_id, auto_id, tipo_compra, monto_fisco,
                            nombre_comprador, dni_comprador, contacto_comprador,
                            sucursal_provincia, sucursal_distrito, nombre_vendedor
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                        fecha_venta, vendedor_id, auto_id, tipo_compra, monto_texto,
                        nombre_comprador, dni_comprador, contacto_comprador,
                        vendedor_data[1], vendedor_data[2], vendedor_data[0]
                    )
                
                total_ventas += 1
            
            if total_ventas >= 432:
                break
        
        conn.commit()
        
        logger.info(f"✅ Insertados {total_ventas} registros de ventas")
        logger.info("✅ Datos iniciales cargados correctamente respetando integridad referencial")
        
    except Exception as e:
        logger.error(f"❌ Error al insertar datos iniciales: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()