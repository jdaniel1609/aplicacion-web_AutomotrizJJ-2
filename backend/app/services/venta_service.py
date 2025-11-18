from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from app.database import get_db_connection, db_manager

logger = logging.getLogger(__name__)


def get_all_ventas(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Obtiene todas las ventas con información detallada
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                v.id,
                v.fecha,
                v.vehiculo,
                v.modelo,
                v.annio,
                v.precio,
                v.nombre_completo as cliente,
                v.dni as cliente_dni,
                vend.nombre || ' ' || vend.apellido as vendedor,
                vend.codigo as vendedor_codigo,
                t.nombre as tienda,
                t.distrito,
                t.provincia,
                t.departamento
            FROM ventas v
            LEFT JOIN vendedor vend ON v.vendedor = vend.codigo
            LEFT JOIN tiendas t ON v.tienda = t.codigo
            ORDER BY v.fecha DESC
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            # Convertir filas de pyodbc a diccionarios
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener ventas: {e}")
        return []
    finally:
        conn.close()


def get_venta_by_id(venta_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene una venta específica por su ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                v.id,
                v.fecha,
                v.vehiculo,
                v.modelo,
                v.annio,
                v.precio,
                v.nombre_completo as cliente,
                v.dni as cliente_dni,
                vend.nombre || ' ' || vend.apellido as vendedor,
                vend.codigo as vendedor_codigo,
                t.nombre as tienda,
                t.distrito,
                t.provincia,
                t.departamento
            FROM ventas v
            LEFT JOIN vendedor vend ON v.vendedor = vend.codigo
            LEFT JOIN tiendas t ON v.tienda = t.codigo
            WHERE v.id = ?
        '''
        
        cursor.execute(query, (venta_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        if db_manager.db_type == "sqlite":
            return dict(row)
        else:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        
    except Exception as e:
        logger.error(f"❌ Error al obtener venta: {e}")
        return None
    finally:
        conn.close()


def create_venta(venta_data: Dict[str, Any]) -> Optional[int]:
    """
    Crea una nueva venta
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if db_manager.db_type == "sqlite":
            cursor.execute('''
                INSERT INTO ventas (fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                venta_data['fecha'],
                venta_data['tienda'],
                venta_data['vendedor'],
                venta_data['vehiculo'],
                venta_data['modelo'],
                venta_data['annio'],
                venta_data['precio'],
                venta_data['dni'],
                venta_data['nombre_completo']
            ))
        else:
            cursor.execute('''
                INSERT INTO ventas (fecha, tienda, vendedor, vehiculo, modelo, annio, precio, dni, nombre_completo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                venta_data['fecha'],
                venta_data['tienda'],
                venta_data['vendedor'],
                venta_data['vehiculo'],
                venta_data['modelo'],
                venta_data['annio'],
                venta_data['precio'],
                venta_data['dni'],
                venta_data['nombre_completo']
            )
        
        conn.commit()
        venta_id = cursor.lastrowid if db_manager.db_type == "sqlite" else cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        logger.info(f"✅ Venta creada con ID: {venta_id}")
        return venta_id
        
    except Exception as e:
        logger.error(f"❌ Error al crear venta: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def get_vehiculos(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de vehículos disponibles
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT id, vehiculo, modelo, annio, precio
            FROM vehiculos
            ORDER BY vehiculo, modelo, annio
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener vehículos: {e}")
        return []
    finally:
        conn.close()


def get_vendedores() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de vendedores
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT codigo, nombre, apellido
            FROM vendedor
            ORDER BY nombre, apellido
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener vendedores: {e}")
        return []
    finally:
        conn.close()


def get_tiendas() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de tiendas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT codigo, nombre, distrito, provincia, departamento
            FROM tiendas
            ORDER BY nombre
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener tiendas: {e}")
        return []
    finally:
        conn.close()


def get_clientes() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de clientes
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT dni, nombre, apellido
            FROM clientes
            ORDER BY nombre, apellido
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener clientes: {e}")
        return []
    finally:
        conn.close()


def get_ventas_by_vendedor(vendedor_codigo: int) -> List[Dict[str, Any]]:
    """
    Obtiene todas las ventas de un vendedor específico
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = '''
            SELECT 
                v.id,
                v.fecha,
                v.vehiculo,
                v.modelo,
                v.annio,
                v.precio,
                v.nombre_completo as cliente,
                v.dni as cliente_dni,
                vend.nombre || ' ' || vend.apellido as vendedor,
                t.nombre as tienda
            FROM ventas v
            LEFT JOIN vendedor vend ON v.vendedor = vend.codigo
            LEFT JOIN tiendas t ON v.tienda = t.codigo
            WHERE v.vendedor = ?
            ORDER BY v.fecha DESC
        '''
        
        cursor.execute(query, (vendedor_codigo,))
        rows = cursor.fetchall()
        
        if db_manager.db_type == "sqlite":
            return [dict(row) for row in rows]
        else:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error al obtener ventas por vendedor: {e}")
        return []
    finally:
        conn.close()


def get_ventas_statistics() -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de ventas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total de ventas
        cursor.execute('SELECT COUNT(*) FROM ventas')
        total_ventas = cursor.fetchone()[0]
        
        # Total vendido
        cursor.execute('SELECT SUM(precio) FROM ventas')
        total_vendido = cursor.fetchone()[0] or 0
        
        # Vehículo más vendido
        cursor.execute('''
            SELECT vehiculo, modelo, COUNT(*) as cantidad
            FROM ventas
            GROUP BY vehiculo, modelo
            ORDER BY cantidad DESC
            LIMIT 1
        ''')
        top_vehiculo = cursor.fetchone()
        
        # Vendedor con más ventas
        cursor.execute('''
            SELECT vend.nombre || ' ' || vend.apellido as vendedor, COUNT(*) as cantidad
            FROM ventas v
            LEFT JOIN vendedor vend ON v.vendedor = vend.codigo
            GROUP BY v.vendedor, vend.nombre, vend.apellido
            ORDER BY cantidad DESC
            LIMIT 1
        ''')
        top_vendedor = cursor.fetchone()
        
        return {
            "total_ventas": total_ventas,
            "total_vendido": float(total_vendido),
            "vehiculo_mas_vendido": {
                "vehiculo": top_vehiculo[0] if top_vehiculo else None,
                "modelo": top_vehiculo[1] if top_vehiculo else None,
                "cantidad": top_vehiculo[2] if top_vehiculo else 0
            },
            "mejor_vendedor": {
                "nombre": top_vendedor[0] if top_vendedor else None,
                "cantidad": top_vendedor[1] if top_vendedor else 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error al obtener estadísticas: {e}")
        return {}
    finally:
        conn.close()