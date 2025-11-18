import sqlite3
import pyodbc
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from contextmanager import contextmanager

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
    Inicializa la base de datos y crea las tablas según el esquema proporcionado.
    Compatible con SQLite y Azure SQL Database.
    
    ESTRUCTURA DE TABLAS:
    =====================
    1. login - Credenciales de usuarios
    2. vehiculos - Catálogo de vehículos disponibles
    3. vendedor - Información de vendedores
    4. clientes - Información de clientes
    5. tiendas - Sucursales/tiendas de la empresa
    6. ventas - Registro de ventas realizadas
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
        
        logger.info("✅ Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {e}")
        raise


def _init_sqlite_database():
    """Inicializa la base de datos SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabla login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login (
                usuario TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        ''')
        
        # Tabla vehiculos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehiculo TEXT NOT NULL,
                modelo TEXT NOT NULL,
                annio INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        
        # Tabla vendedor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendedor (
                codigo INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL
            )
        ''')
        
        # Tabla clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                dni TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL
            )
        ''')
        
        # Tabla tiendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tiendas (
                codigo INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                distrito TEXT NOT NULL,
                provincia TEXT NOT NULL,
                departamento TEXT NOT NULL
            )
        ''')
        
        # Tabla ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                tienda INTEGER NOT NULL,
                vendedor INTEGER NOT NULL,
                vehiculo TEXT NOT NULL,
                modelo TEXT NOT NULL,
                annio INTEGER NOT NULL,
                precio REAL NOT NULL,
                dni TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                FOREIGN KEY (tienda) REFERENCES tiendas(codigo),
                FOREIGN KEY (vendedor) REFERENCES vendedor(codigo),
                FOREIGN KEY (dni) REFERENCES clientes(dni)
            )
        ''')
        
        conn.commit()
        logger.info("✅ Tablas SQLite creadas correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al crear tablas SQLite: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_azure_database():
    """Inicializa la base de datos Azure SQL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabla login
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'login')
            CREATE TABLE login (
                usuario NVARCHAR(50) PRIMARY KEY,
                password NVARCHAR(50) NOT NULL
            )
        ''')
        
        # Tabla vehiculos
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'vehiculos')
            CREATE TABLE vehiculos (
                id INT PRIMARY KEY IDENTITY(1,1),
                vehiculo NVARCHAR(100) NOT NULL,
                modelo NVARCHAR(100) NOT NULL,
                annio INT NOT NULL,
                precio DECIMAL(10,2) NOT NULL
            )
        ''')
        
        # Tabla vendedor
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'vendedor')
            CREATE TABLE vendedor (
                codigo INT PRIMARY KEY,
                nombre NVARCHAR(50) NOT NULL,
                apellido NVARCHAR(50) NOT NULL
            )
        ''')
        
        # Tabla clientes
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'clientes')
            CREATE TABLE clientes (
                dni NVARCHAR(15) PRIMARY KEY,
                nombre NVARCHAR(50) NOT NULL,
                apellido NVARCHAR(50) NOT NULL
            )
        ''')
        
        # Tabla tiendas
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tiendas')
            CREATE TABLE tiendas (
                codigo INT PRIMARY KEY,
                nombre NVARCHAR(100) NOT NULL,
                distrito NVARCHAR(100) NOT NULL,
                provincia NVARCHAR(100) NOT NULL,
                departamento NVARCHAR(100) NOT NULL
            )
        ''')
        
        # Tabla ventas
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ventas')
            CREATE TABLE ventas (
                id INT PRIMARY KEY IDENTITY(1,1),
                fecha DATE NOT NULL,
                tienda INT NOT NULL,
                vendedor INT NOT NULL,
                vehiculo NVARCHAR(100) NOT NULL,
                modelo NVARCHAR(100) NOT NULL,
                annio INT NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                dni NVARCHAR(15) NOT NULL,
                nombre_completo NVARCHAR(120) NOT NULL,
                FOREIGN KEY (tienda) REFERENCES tiendas(codigo),
                FOREIGN KEY (vendedor) REFERENCES vendedor(codigo),
                FOREIGN KEY (dni) REFERENCES clientes(dni)
            )
        ''')
        
        conn.commit()
        logger.info("✅ Tablas Azure SQL creadas correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al crear tablas Azure SQL: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def seed_initial_data():
    """Inserta datos iniciales en la base de datos según el script proporcionado"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM login")
        result = cursor.fetchone()
        count = result[0] if db_manager.db_type == "azure" else result[0]
        
        if count > 0:
            logger.info("Los datos iniciales ya existen, omitiendo seed...")
            return
        
        logger.info("📝 Insertando datos iniciales...")
        
        # TABLA LOGIN
        login_data = [
            ('ochavez', '123456'),
            ('csoto', '123456')
        ]
        
        for usuario, password in login_data:
            if db_manager.db_type == "sqlite":
                cursor.execute('INSERT INTO login (usuario, password) VALUES (?, ?)', 
                             (usuario, password))
            else:
                cursor.execute('INSERT INTO login (usuario, password) VALUES (?, ?)', 
                             usuario, password)
        
        logger.info(f"✅ Insertados {len(login_data)} usuarios en login")
        
        # TABLA VEHICULOS (continúa con todos los datos del script...)
        vehiculos_data = [
            ('Toyota', 'Corolla', 2018, 14500.00),
            ('Toyota', 'Yaris', 2020, 13000.00),
            ('Toyota', 'Hilux', 2021, 28000.00),
            ('Toyota', 'RAV4', 2019, 24000.00),
            ('Honda', 'Civic', 2017, 13500.00),
            ('Honda', 'CR-V', 2021, 26000.00),
            ('Honda', 'Fit', 2018, 11000.00),
            ('Mazda', 'Mazda3', 2020, 17000.00),
            ('Mazda', 'CX-5', 2019, 22000.00),
            ('Mazda', 'Mazda6', 2017, 16000.00),
            ('Nissan', 'Sentra', 2018, 12500.00),
            ('Nissan', 'Versa', 2020, 11500.00),
            ('Nissan', 'X-Trail', 2021, 25000.00),
            ('Nissan', 'Frontier', 2019, 23000.00),
            ('Hyundai', 'Elantra', 2017, 12000.00),
            ('Hyundai', 'Tucson', 2021, 25000.00),
            ('Hyundai', 'Santa Fe', 2018, 21000.00),
            ('Kia', 'Rio', 2020, 11500.00),
            ('Kia', 'Sportage', 2019, 20000.00),
            ('Kia', 'Sorento', 2017, 18000.00),
            ('Chevrolet', 'Spark', 2018, 9000.00),
            ('Chevrolet', 'Cruze', 2019, 16000.00),
            ('Chevrolet', 'Tracker', 2021, 23000.00),
            ('Chevrolet', 'Equinox', 2020, 24000.00),
            ('Ford', 'Fiesta', 2017, 9500.00),
            ('Ford', 'Focus', 2018, 13000.00),
            ('Ford', 'Ranger', 2021, 30000.00),
            ('Ford', 'Escape', 2019, 22000.00),
            ('Volkswagen', 'Gol', 2020, 10500.00),
            ('Volkswagen', 'Jetta', 2019, 18000.00),
            ('Volkswagen', 'Tiguan', 2021, 26000.00),
            ('Volkswagen', 'Amarok', 2018, 27000.00),
            ('Subaru', 'Forester', 2020, 25000.00),
            ('Subaru', 'Impreza', 2018, 15000.00),
            ('Subaru', 'Outback', 2021, 28000.00),
            ('BMW', 'X1', 2019, 33000.00),
            ('BMW', '320i', 2018, 28000.00),
            ('BMW', 'X3', 2020, 42000.00),
            ('Mercedes-Benz', 'C200', 2017, 30000.00),
            ('Mercedes-Benz', 'GLA200', 2019, 35000.00),
            ('Mercedes-Benz', 'A200', 2020, 33000.00),
            ('Audi', 'A3', 2018, 26000.00),
            ('Audi', 'Q3', 2020, 35000.00),
            ('Audi', 'A4', 2021, 40000.00),
            ('Jeep', 'Renegade', 2019, 22000.00),
            ('Jeep', 'Compass', 2020, 26000.00),
            ('Jeep', 'Wrangler', 2021, 45000.00),
            ('Renault', 'Logan', 2018, 9000.00),
            ('Renault', 'Duster', 2020, 15000.00),
            ('Peugeot', '3008', 2019, 23000.00)
        ]
        
        for vehiculo, modelo, annio, precio in vehiculos_data:
            if db_manager.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO vehiculos (vehiculo, modelo, annio, precio) 
                    VALUES (?, ?, ?, ?)
                ''', (vehiculo, modelo, annio, precio))
            else:
                cursor.execute('''
                    INSERT INTO vehiculos (vehiculo, modelo, annio, precio) 
                    VALUES (?, ?, ?, ?)
                ''', vehiculo, modelo, annio, precio)
        
        logger.info(f"✅ Insertados {len(vehiculos_data)} vehículos")
        
        # TABLA VENDEDOR
        vendedor_data = [
            (1, 'Carlos', 'Gomez'),
            (2, 'Luis', 'Fernandez'),
            (3, 'Ana', 'Ramirez'),
            (4, 'Maria', 'Torres'),
            (5, 'Jorge', 'Paredes'),
            (6, 'Lucia', 'Mendoza'),
            (7, 'Pedro', 'Caceres'),
            (8, 'Sofia', 'Vargas'),
            (9, 'Andres', 'Lopez'),
            (10, 'Valeria', 'Salazar')
        ]
        
        for codigo, nombre, apellido in vendedor_data:
            if db_manager.db_type == "sqlite":
                cursor.execute('INSERT INTO vendedor (codigo, nombre, apellido) VALUES (?, ?, ?)', 
                             (codigo, nombre, apellido))
            else:
                cursor.execute('INSERT INTO vendedor (codigo, nombre, apellido) VALUES (?, ?, ?)', 
                             codigo, nombre, apellido)
        
        logger.info(f"✅ Insertados {len(vendedor_data)} vendedores")
        
        # TABLA CLIENTES
        clientes_data = [
            ('70123451', 'Carlos', 'Gomez'),
            ('70234512', 'Luis', 'Fernandez'),
            ('70345623', 'Ana', 'Ramirez'),
            ('70456734', 'Maria', 'Torres'),
            ('70567845', 'Jorge', 'Paredes'),
            ('70678956', 'Lucia', 'Mendoza'),
            ('70789067', 'Pedro', 'Caceres'),
            ('70890178', 'Sofia', 'Vargas'),
            ('70901289', 'Andres', 'Lopez'),
            ('71012390', 'Valeria', 'Salazar'),
            ('71123401', 'Miguel', 'Reyes'),
            ('71234502', 'Paola', 'Montoya'),
            ('71345603', 'Ricardo', 'Sanchez'),
            ('71456704', 'Fiorella', 'Diaz'),
            ('71567805', 'Hector', 'Vera'),
            ('71678906', 'Camila', 'Rojas'),
            ('71789007', 'Daniel', 'Quispe'),
            ('71890108', 'Rosa', 'Huaman'),
            ('71901209', 'Fernando', 'Vilca'),
            ('72012310', 'Mariana', 'Castillo')
        ]
        
        for dni, nombre, apellido in clientes_data:
            if db_manager.db_type == "sqlite":
                cursor.execute('INSERT INTO clientes (dni, nombre, apellido) VALUES (?, ?, ?)', 
                             (dni, nombre, apellido))
            else:
                cursor.execute('INSERT INTO clientes (dni, nombre, apellido) VALUES (?, ?, ?)', 
                             dni, nombre, apellido)
        
        logger.info(f"✅ Insertados {len(clientes_data)} clientes")
        
        # TABLA TIENDAS
        tiendas_data = [
            (1, 'Tienda Central', 'Miraflores', 'Lima', 'Lima'),
            (2, 'Comercial Norte', 'Los Olivos', 'Lima', 'Lima'),
            (3, 'Market Sur', 'Santiago', 'Cusco', 'Cusco'),
            (4, 'Plaza Este', 'Yanahuara', 'Arequipa', 'Arequipa'),
            (5, 'Super Centro', 'Trujillo', 'Trujillo', 'La Libertad')
        ]
        
        for codigo, nombre, distrito, provincia, departamento in tiendas_data:
            if db_manager.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO tiendas (codigo, nombre, distrito, provincia, departamento) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (codigo, nombre, distrito, provincia, departamento))
            else:
                cursor.execute('''
                    INSERT INTO tiendas (codigo, nombre, distrito, provincia, departamento) 
                    VALUES (?, ?, ?, ?, ?)
                ''', codigo, nombre, distrito, provincia, departamento)
        
        logger.info(f"✅ Insertadas {len(tiendas_data)} tiendas")
        
        conn.commit()
        
        # TABLA VENTAS - Insertar 100 registros aleatorios usando CROSS JOIN
        logger.info("📝 Generando ventas aleatorias...")
        
        cursor.execute('SELECT codigo FROM tiendas')
        tiendas = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT codigo FROM vendedor')
        vendedores = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT vehiculo, modelo, annio, precio FROM vehiculos')
        vehiculos = cursor.fetchall()
        
        cursor.execute('SELECT dni, nombre, apellido FROM clientes')
        clientes = cursor.fetchall()
        
        ventas_count = 0
        max_ventas = 100
        
        for tienda in tiendas:
            for vendedor in vendedores:
                for vehiculo_data in vehiculos:
                    for cliente_data in clientes:
                        if ventas_count >= max_ventas:
                            break
                        
                        # Generar fecha aleatoria en los últimos 2 años
                        dias_atras = random.randint(0, 730)
                        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
                        
                        if db_manager.db_type == "sqlite":
                            vehiculo, modelo, annio, precio = vehiculo_data
                            dni = cliente_data[0]
                            nombre_completo = f"{cliente_data[1]} {cliente_data[2]}"
                        else:
                            vehiculo, modelo, annio, precio = vehiculo_data
                            dni = cliente_data[0]
                            nombre_completo = f"{cliente_data[1]} {cliente_data[2]}"
                        
                        if db_manager.db_type == "sqlite":
                            cursor.execute('''
                                INSERT INTO ventas (fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo))
                        else:
                            cursor.execute('''
                                INSERT INTO ventas (fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo)
                        
                        ventas_count += 1
                    
                    if ventas_count >= max_ventas:
                        break
                if ventas_count >= max_ventas:
                    break
            if ventas_count >= max_ventas:
                break
        
        conn.commit()
        
        logger.info(f"✅ Insertadas {ventas_count} ventas")
        logger.info("✅ Datos iniciales cargados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al insertar datos iniciales: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()