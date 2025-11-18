from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import date

from app.routes.auth import get_current_user
from app.services import venta_service

router = APIRouter()


# Modelos Pydantic
class VentaBase(BaseModel):
    fecha: date
    tienda: int
    vendedor: int
    vehiculo: str
    modelo: str
    annio: int
    precio: float
    dni: str
    nombre_completo: str


class VentaCreate(VentaBase):
    pass


class VentaResponse(VentaBase):
    id: int
    
    class Config:
        from_attributes = True


class VentaDetailResponse(BaseModel):
    id: int
    fecha: date
    vehiculo: str
    modelo: str
    annio: int
    precio: float
    cliente: str
    cliente_dni: str
    vendedor: str
    vendedor_codigo: int
    tienda: str
    distrito: str
    provincia: str
    departamento: str


class VehiculoResponse(BaseModel):
    id: int
    vehiculo: str
    modelo: str
    annio: int
    precio: float


class VendedorResponse(BaseModel):
    codigo: int
    nombre: str
    apellido: str


class TiendaResponse(BaseModel):
    codigo: int
    nombre: str
    distrito: str
    provincia: str
    departamento: str


class ClienteResponse(BaseModel):
    dni: str
    nombre: str
    apellido: str


class VentasStatisticsResponse(BaseModel):
    total_ventas: int
    total_vendido: float
    vehiculo_mas_vendido: dict
    mejor_vendedor: dict


@router.get("/ventas", response_model=List[VentaDetailResponse])
async def get_ventas(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la lista de ventas con paginación
    """
    ventas = venta_service.get_all_ventas(limit=limit, offset=offset)
    return ventas


@router.get("/ventas/{venta_id}", response_model=VentaDetailResponse)
async def get_venta(
    venta_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene una venta específica por su ID
    """
    venta = venta_service.get_venta_by_id(venta_id)
    
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    return venta


@router.post("/ventas", response_model=VentaResponse, status_code=201)
async def create_venta(
    venta: VentaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una nueva venta
    """
    venta_data = venta.dict()
    venta_id = venta_service.create_venta(venta_data)
    
    if not venta_id:
        raise HTTPException(status_code=500, detail="Error al crear la venta")
    
    return {**venta_data, "id": venta_id}


@router.get("/vehiculos", response_model=List[VehiculoResponse])
async def get_vehiculos(
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la lista de vehículos disponibles
    """
    vehiculos = venta_service.get_vehiculos(limit=limit)
    return vehiculos


@router.get("/vendedores", response_model=List[VendedorResponse])
async def get_vendedores(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la lista de vendedores
    """
    vendedores = venta_service.get_vendedores()
    return vendedores


@router.get("/tiendas", response_model=List[TiendaResponse])
async def get_tiendas(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la lista de tiendas
    """
    tiendas = venta_service.get_tiendas()
    return tiendas


@router.get("/clientes", response_model=List[ClienteResponse])
async def get_clientes(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la lista de clientes
    """
    clientes = venta_service.get_clientes()
    return clientes


@router.get("/ventas/vendedor/{vendedor_codigo}", response_model=List[VentaDetailResponse])
async def get_ventas_by_vendedor(
    vendedor_codigo: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene todas las ventas de un vendedor específico
    """
    ventas = venta_service.get_ventas_by_vendedor(vendedor_codigo)
    return ventas


@router.get("/statistics", response_model=VentasStatisticsResponse)
async def get_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas generales de ventas
    """
    stats = venta_service.get_ventas_statistics()
    return stats