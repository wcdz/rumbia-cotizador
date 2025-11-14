from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ParametrosCotizacion(BaseModel):
    """Modelo para los parámetros de la cotización"""
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
    
    class Config:
        from_attributes = True

