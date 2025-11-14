import sqlite3
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DATABASE_PATH = "automotriz_jj.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # IMPORTANTE: Habilitar foreign keys en SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    """
    Inicializa la base de datos y crea las tablas con sus relaciones
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("📊 Creando estructura de base de datos...")
        
        # ============================================
        # TABLA 1: vendedores (Tabla Principal)
        # ============================================
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
                
                -- Constraints adicionales
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
        
        # ============================================
        # TABLA 2: autos_disponibles (Tabla Principal)
        # ============================================
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
                
                -- Constraints adicionales
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
        
        # ============================================
        # TABLA 3: registro_venta (Tabla con Foreign Keys)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- FOREIGN KEY 1: Relación con vendedores
                vendedor_id INTEGER NOT NULL,
                
                -- FOREIGN KEY 2: Relación con autos_disponibles
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
                
                -- Definición explícita de FOREIGN KEYS
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
                
                -- Constraints adicionales
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
        
        logger.info("✅ Tabla 'registro_venta' creada con FOREIGN KEYS:")
        logger.info("   - FK: vendedor_id → vendedores(id)")
        logger.info("   - FK: auto_id → autos_disponibles(id)")
        conn.commit()
        logger.info("✅ Base de datos inicializada correctamente con todas las relaciones")
        
        # Verificar integridad de foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if fk_errors:
            logger.error(f"❌ Errores de integridad referencial: {fk_errors}")
        else:
            logger.info("✅ Integridad referencial verificada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def seed_initial_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM vendedores")
        if cursor.fetchone()[0] > 0:
            logger.info("Los datos iniciales ya existen, omitiendo seed...")
            return
        
        import hashlib
        
        logger.info("📝 Insertando datos iniciales...")
        
        # PASO 1: Insertar VENDEDORES (Tabla padre) #
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
            cursor.execute('''
                INSERT INTO vendedores (username, password_hash, full_name, email, role, codigo_vendedor, sucursal_provincia, sucursal_distrito)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, role, codigo, provincia, distrito))
        
        logger.info(f"✅ Insertados {len(vendedores)} vendedores")
        
        # PASO 2: Insertar AUTOS (Tabla padre) #
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
            cursor.execute('''
                INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (marca, modelo, 2024, precio, 25))
        # Autos 2025
        for marca, modelo, precio_2024 in autos_base:
            incremento = random.randrange(25000, 75001, 10)
            precio_2025 = precio_2024 + incremento
            cursor.execute('''
                INSERT INTO autos_disponibles (marca, modelo, anio, precio_referencial, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (marca, modelo, 2025, precio_2025, 25))
        
        logger.info(f"✅ Insertados {len(autos_base) * 2} autos (2024 y 2025)")
        conn.commit()
        
        # PASO 3: Insertar VENTAS (Tabla con FK) #
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
                monto = int(precio_base * variacion)
                monto_texto = f"S/. {monto:,.2f}"
                
                dias_atras = random.randint(0, 180)
                fecha_venta = fecha_inicio + timedelta(days=dias_atras)
                
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