from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


class ParametrosCotizacion(BaseModel):
    """Modelo para los parámetros de la cotización"""
    edad_actuarial: int = Field(..., ge=0, description="Edad actuarial del cliente")
    sexo: Literal["M", "F"] = Field(..., description="Sexo del cliente (M o F)")
    prima: float = Field(..., ge=0, description="Prima del seguro")
    periodo_pago: int = Field(..., ge=1, description="Periodo de pago")


class ParametrosCotizacionSinPeriodo(BaseModel):
    """Modelo para los parámetros de la cotización sin periodo (para colecciones)"""
    edad_actuarial: int = Field(..., ge=0, description="Edad actuarial del cliente")
    sexo: Literal["M", "F"] = Field(..., description="Sexo del cliente (M o F)")
    prima: float = Field(..., ge=0, description="Prima del seguro")


class CotizacionBase(BaseModel):
    """Modelo base para cotizaciones"""
    producto: str = Field(..., min_length=1, description="Nombre del producto")
    parametros: ParametrosCotizacion = Field(..., description="Parámetros de la cotización")


class CotizacionCreate(CotizacionBase):
    """Modelo para crear una nueva cotización"""
    pass


class CotizacionResponse(CotizacionBase):
    """Modelo de respuesta para cotizaciones"""
    id: int
    fecha_creacion: datetime
    porcentaje_devolucion: Optional[float] = Field(None, description="Porcentaje de devolución calculado (C11)")
    tasa_implicita: Optional[float] = Field(None, description="Tasa implícita calculada (C21)")
    suma_asegurada: Optional[float] = Field(None, description="Suma asegurada (C10)")
    devolucion: Optional[float] = Field(None, description="Devolución calculada (C29)")
    prima_anual: Optional[float] = Field(None, description="Prima anual calculada (C30)")
    tabla_devolucion: Optional[str] = Field(None, description="Tabla de devolución basada en el periodo de pago (array en formato string)")
    
    class Config:
        from_attributes = True


# Schemas para cotizaciones por colección
class CotizacionColeccionRequest(BaseModel):
    """Request para cotizaciones por colección"""
    producto: str = Field(..., min_length=1, description="Nombre del producto")
    parametros: ParametrosCotizacionSinPeriodo = Field(..., description="Parámetros de la cotización")


class CotizacionDetalle(BaseModel):
    """Detalle de una cotización individual"""
    porcentaje_devolucion: Optional[str] = Field(None, description="Porcentaje de devolución")
    trea: Optional[str] = Field(None, description="Tasa de rendimiento efectiva anual")
    aporte_total: Optional[str] = Field(None, description="Aporte total")
    ganancia_total: Optional[str] = Field(None, description="Ganancia total")
    devolucion_total: Optional[str] = Field(None, description="Devolución total")
    rentabilidad: Optional[str] = Field(None, description="Rentabilidad")
    tabla_devolucion: Optional[str] = Field(None, description="Tabla de devolución")


class CotizacionPorPeriodo(BaseModel):
    """Cotización para un periodo específico"""
    periodo: int = Field(..., description="Periodo de pago en años")
    cotizacion: CotizacionDetalle = Field(..., description="Detalle de la cotización")


class CotizacionColeccionResponse(BaseModel):
    """Respuesta para cotizaciones por colección"""
    prima: float = Field(..., description="Prima solicitada")
    periodos_disponibles: List[int] = Field(..., description="Periodos disponibles para esta prima")
    cotizaciones: List[CotizacionPorPeriodo] = Field(..., description="Lista de cotizaciones por periodo")
    total_cotizaciones: int = Field(..., description="Total de cotizaciones generadas")
    imagen_base64: Optional[str] = Field(None, description="URL temporal de la imagen (válida por 10 minutos)")


# Schemas para generación de imágenes
class ImageGenerationRequest(BaseModel):
    """Request para generar imagen de cotización"""
    producto: str = Field(..., min_length=1, description="Nombre del producto")
    parametros: ParametrosCotizacionSinPeriodo = Field(..., description="Parámetros de la cotización")
    nombre_archivo: Optional[str] = Field(None, description="Nombre opcional para el archivo (sin extensión)")


class ImageGenerationResponse(BaseModel):
    """Respuesta para generación de imagen"""
    ruta_archivo: str = Field(..., description="Ruta del archivo generado")
    nombre_archivo: str = Field(..., description="Nombre del archivo generado")
    mensaje: str = Field(..., description="Mensaje de confirmación")
