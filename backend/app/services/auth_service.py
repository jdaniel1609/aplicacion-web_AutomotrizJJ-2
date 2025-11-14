from typing import Optional
import hashlib
import logging
from app.database import get_db_connection

logger = logging.getLogger(__name__)


def simple_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificación simple de contraseña"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autentica un usuario verificando sus credenciales en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, password_hash, full_name, email, role, 
                   codigo_vendedor, sucursal_provincia, sucursal_distrito, is_active
            FROM vendedores
            WHERE username = ?
        ''', (username,))
        
        user_row = cursor.fetchone()
        
        if not user_row:
            logger.warning(f"❌ Usuario no encontrado: {username}")
            return None
        
        user = dict(user_row)
        
        if not simple_verify_password(password, user["password_hash"]):
            logger.warning(f"❌ Contraseña incorrecta para usuario: {username}")
            return None
        
        if not user.get("is_active", 0):
            logger.warning(f"❌ Usuario inactivo: {username}")
            return None
        
        logger.info(f"✅ Autenticación exitosa para usuario: {username}")
        return user
        
    except Exception as e:
        logger.error(f"❌ Error al autenticar usuario: {e}")
        return None
    finally:
        conn.close()


def get_user(username: str) -> Optional[dict]:
    """Obtiene un usuario por su nombre de usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, full_name, email, role, 
                   codigo_vendedor, sucursal_provincia, sucursal_distrito, is_active
            FROM vendedores
            WHERE username = ?
        ''', (username,))
        
        user_row = cursor.fetchone()
        
        if user_row:
            return dict(user_row)
        return None
        
    except Exception as e:
        logger.error(f"❌ Error al obtener usuario: {e}")
        return None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Obtiene un usuario por su ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, full_name, email, role, 
                   codigo_vendedor, sucursal_provincia, sucursal_distrito, is_active
            FROM vendedores
            WHERE id = ?
        ''', (user_id,))
        
        user_row = cursor.fetchone()
        
        if user_row:
            return dict(user_row)
        return None
        
    except Exception as e:
        logger.error(f"❌ Error al obtener usuario por ID: {e}")
        return None
    finally:
        conn.close()