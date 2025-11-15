from fastapi import APIRouter, status
from typing import Dict
from app.schemas.cotizacion import (
    CotizacionCreate, 
    CotizacionResponse,
    CotizacionColeccionRequest,
    CotizacionColeccionResponse,
    ImageGenerationRequest,
    ImageGenerationResponse
)
import os
from app.services.image_service import ImageService

# Importar el servicio de cotizaciones (sin dependencias de Excel/LibreOffice)
from app.services.cotizacion_service import CotizacionService

router = APIRouter()
service = CotizacionService()
image_service = ImageService()


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


@router.post("/cotizaciones/generar-imagen", response_model=ImageGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generar_imagen_cotizacion(request: ImageGenerationRequest):
    """
    Genera una imagen con gráfico y tabla de cotizaciones
    
    Crea un gráfico mostrando la evolución de devolución por periodo y una tabla resumen.
    La imagen se guarda en formato JPEG en la carpeta 'db'.
    """
    # Generar la imagen
    ruta_archivo, _ = image_service.generar_grafico_desde_endpoint(
        prima=request.parametros.prima,
        edad_actuarial=request.parametros.edad_actuarial,
        sexo=request.parametros.sexo,
        retornar_base64=False
    )
    
    # Obtener nombre del archivo
    nombre_archivo = os.path.basename(ruta_archivo)
    
    return ImageGenerationResponse(
        ruta_archivo=ruta_archivo,
        nombre_archivo=nombre_archivo,
        mensaje=f"Imagen generada exitosamente: {nombre_archivo}"
    )


@router.delete("/cotizaciones/cache", status_code=status.HTTP_200_OK)
async def limpiar_cache() -> Dict:
    """
    Limpia el cache de colecciones de cotizaciones
    
    Útil cuando se actualizan los datos del Excel o configuraciones.
    """
    cantidad = service.limpiar_cache_colecciones()
    return {
        "mensaje": "Cache limpiado exitosamente",
        "elementos_eliminados": cantidad
    }


@router.get("/cotizaciones/cache/estadisticas", status_code=status.HTTP_200_OK)
async def obtener_estadisticas_cache() -> Dict:
    """
    Obtiene estadísticas del cache
    
    Muestra cuántos elementos hay en cache actualmente.
    """
    stats = service.obtener_estadisticas_cache()
    return {
        "estadisticas": stats,
        "mensaje": "Estadísticas obtenidas exitosamente"
    }

