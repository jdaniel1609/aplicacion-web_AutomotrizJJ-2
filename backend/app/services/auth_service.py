from typing import Optional
import logging
from app.database import get_db_connection, db_manager

logger = logging.getLogger(__name__)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autentica un usuario verificando sus credenciales en la tabla login
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT usuario, password
            FROM login
            WHERE usuario = ?
        ''', (username,))
        
        user_row = cursor.fetchone()
        
        if not user_row:
            logger.warning(f"❌ Usuario no encontrado: {username}")
            return None
        
        if db_manager.db_type == "sqlite":
            user = dict(user_row)
            stored_password = user["password"]
        else:
            stored_password = user_row[1]
        
        # Verificación simple de contraseña (sin hash)
        if password != stored_password:
            logger.warning(f"❌ Contraseña incorrecta para usuario: {username}")
            return None
        
        logger.info(f"✅ Autenticación exitosa para usuario: {username}")
        
        # Retornar datos del usuario
        return {
            "usuario": username,
            "authenticated": True
        }
        
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
            SELECT usuario
            FROM login
            WHERE usuario = ?
        ''', (username,))
        
        user_row = cursor.fetchone()
        
        if user_row:
            return {
                "usuario": username if db_manager.db_type == "sqlite" else user_row[0],
                "exists": True
            }
        return None
        
    except Exception as e:
        logger.error(f"❌ Error al obtener usuario: {e}")
        return None
    finally:
        conn.close()