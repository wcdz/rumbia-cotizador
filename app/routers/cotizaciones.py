from fastapi import APIRouter, status
from app.schemas.cotizacion import (
    CotizacionCreate, 
    CotizacionResponse,
    CotizacionColeccionRequest,
    CotizacionColeccionResponse
)
from app.services.cotizacion_service import CotizacionService

router = APIRouter()
service = CotizacionService()


@router.post("/cotizaciones", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_cotizacion(cotizacion: CotizacionCreate):
    """Crear una nueva cotización"""
    return service.crear(cotizacion)


@router.post("/cotizaciones/coleccion", response_model=CotizacionColeccionResponse, status_code=status.HTTP_200_OK)
async def crear_cotizacion_coleccion(request: CotizacionColeccionRequest):
    """
    Crear cotizaciones para todos los periodos disponibles de una prima específica
    
    Genera múltiples cotizaciones basadas en los periodos configurados para la prima solicitada.
    """
    return service.crear_cotizacion_coleccion(request)

