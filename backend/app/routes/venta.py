import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from pydantic import BaseModel, Field
from app.services.venta_service import (
    get_autos_disponibles,
    registrar_venta,
    get_ventas_by_vendedor
)
from app.services.auth_service import get_user
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/venta", tags=["Ventas"])


class VentaCreate(BaseModel):
    """Esquema para crear una venta"""
    auto_id: int = Field(..., description="ID del auto")
    tipo_compra: str = Field(..., pattern="^(Cash|Crédito)$", description="Tipo de compra: Cash o Crédito")
    monto_fisco: str = Field(..., min_length=1, description="Monto de la venta")
    nombre_comprador: str = Field(..., min_length=3, description="Nombre del comprador")
    dni_comprador: str = Field(..., min_length=8, max_length=8, description="DNI del comprador")
    contacto_comprador: str = Field(..., min_length=6, description="Contacto del comprador")


@router.get("/autos")
async def listar_autos(
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    current_user: dict = Depends(get_current_user)
):
    """Lista autos disponibles con búsqueda opcional"""
    logger.info(f"Listando autos - Usuario: {current_user['username']}, Búsqueda: {search}")
    
    autos = get_autos_disponibles(search)
    
    return {
        "total": len(autos),
        "autos": autos
    }


@router.post("/registrar")
async def crear_venta(
    venta: VentaCreate,
    current_user: dict = Depends(get_current_user)
):
    """Registra una nueva venta"""
    username = current_user["username"]
    user = get_user(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    logger.info(f"Registrando venta - Vendedor: {user['full_name']} ({user['sucursal_provincia']}/{user['sucursal_distrito']})")
    
    # Registrar la venta
    venta_id = registrar_venta(
        vendedor_id=user['id'],
        auto_id=venta.auto_id,
        tipo_compra=venta.tipo_compra,
        monto_fisco=venta.monto_fisco,
        nombre_comprador=venta.nombre_comprador,
        dni_comprador=venta.dni_comprador,
        contacto_comprador=venta.contacto_comprador,
        sucursal_provincia=user['sucursal_provincia'],
        sucursal_distrito=user['sucursal_distrito'],
        nombre_vendedor=user['full_name']
    )
    
    if not venta_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar la venta"
        )
    
    return {
        "success": True,
        "message": "Venta registrada exitosamente",
        "venta_id": venta_id
    }


@router.get("/mis-ventas")
async def obtener_mis_ventas(
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene las ventas del vendedor actual"""
    username = current_user["username"]
    user = get_user(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    logger.info(f"Obteniendo ventas - Vendedor: {user['full_name']}")
    
    ventas = get_ventas_by_vendedor(user['id'], limit)
    
    return {
        "total": len(ventas),
        "vendedor": user['full_name'],
        "sucursal": f"{user['sucursal_provincia']}/{user['sucursal_distrito']}",
        "ventas": ventas
    }