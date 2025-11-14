import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.services.auth_service import authenticate_user, get_user
from app.utils.security import create_access_token, get_current_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint de login para autenticar usuarios"""
    logger.info(f"Intento de login para usuario: {form_data.username}")
    
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        logger.warning(f"Login fallido para usuario: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login exitoso para usuario: {form_data.username} - Rol: {user.get('role')} - Sucursal: {user.get('sucursal_provincia')}/{user.get('sucursal_distrito')}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user.get("role", "user"),
            "codigo_vendedor": user.get("codigo_vendedor", ""),
            "sucursal_provincia": user.get("sucursal_provincia", ""),
            "sucursal_distrito": user.get("sucursal_distrito", "")
        }
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado actualmente"""
    username = current_user["username"]
    logger.info(f"Solicitud de información de usuario: {username}")
    
    user = get_user(username)
    
    if not user:
        logger.error(f"Usuario no encontrado: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "codigo_vendedor": user.get("codigo_vendedor", ""),
        "sucursal_provincia": user.get("sucursal_provincia", ""),
        "sucursal_distrito": user.get("sucursal_distrito", "")
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Endpoint de logout"""
    logger.info(f"Logout exitoso para usuario: {current_user['username']}")
    return {
        "message": f"Usuario {current_user['username']} ha cerrado sesión exitosamente"
    }