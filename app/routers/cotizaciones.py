from fastapi import APIRouter, status
from app.schemas.cotizacion import CotizacionCreate, CotizacionResponse
from app.services.cotizacion_service import CotizacionService

router = APIRouter()
service = CotizacionService()


@router.post("/cotizaciones", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_cotizacion(cotizacion: CotizacionCreate):
    """Crear una nueva cotización"""
    return service.crear(cotizacion)

