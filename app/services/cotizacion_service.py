"""
Servicio de cotizaciones con algoritmo determinista y progresivo
Sin dependencia de Excel/LibreOffice
"""
import os
import json
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
from app.schemas.cotizacion import (
    CotizacionCreate, 
    CotizacionResponse,
    CotizacionColeccionRequest,
    CotizacionColeccionResponse,
    CotizacionPorPeriodo,
    CotizacionDetalle
)

# Simulación de base de datos en memoria
cotizaciones_db: List[CotizacionResponse] = []
contador_id = 1

# Cache para colecciones de cotizaciones
_colecciones_cache: Dict[str, 'CotizacionColeccionResponse'] = {}


def _generar_cache_key_coleccion(edad_actuarial: int, sexo: str, prima: float) -> str:
    """Genera una clave única para el cache de colecciones"""
    params_str = f"coleccion_{edad_actuarial}_{sexo}_{prima}"
    return hashlib.md5(params_str.encode()).hexdigest()


# Ruta al archivo de configuración de periodos
PERIODOS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    "assets", "configuracion_combinatorias", "periodos_cotizacion.json")


class CotizacionService:
    """Servicio para manejar la lógica de negocio de cotizaciones"""
    
    def _generar_porcentaje_devolucion(self, periodo: int, prima: float, edad: int, sexo: str) -> float:
        """
        Genera un porcentaje de devolución progresivo y atractivo
        A mayor periodo, significativamente mayor porcentaje (incremental)
        """
        # Base inicial que varía según el periodo (más agresivo)
        # Periodo 4: ~115%, Periodo 5: ~120%, Periodo 6: ~125%, Periodo 7: ~132%
        base = 108 + (periodo - 4) * 5.0
        
        # Incremento adicional por periodo (beneficio exponencial por tiempo)
        # Cuanto más tiempo inviertes, mejor es el retorno
        incremento_exponencial = (periodo - 4) ** 1.3 * 1.8
        
        # Ajuste por prima (primas más altas reciben mejor tratamiento)
        # Por cada 100 soles de prima, aumenta 0.3%
        ajuste_prima = (prima / 100) * 0.3
        
        # Ajuste por edad (edades más jóvenes tienen ligeramente mejor retorno)
        # Diferencia máxima de ~2% entre la edad más joven y más vieja
        ajuste_edad = max(0, (45 - edad) * 0.08)
        
        # Bonus por periodo largo (incentivo adicional para periodos 6 y 7)
        bonus_largo_plazo = 0
        if periodo >= 6:
            bonus_largo_plazo = (periodo - 5) * 2.5
        
        # Calcular porcentaje final
        porcentaje = base + incremento_exponencial + ajuste_prima + ajuste_edad + bonus_largo_plazo
        
        # Asegurar que sea incremental y realista (entre 110% y 140%)
        porcentaje = max(110, min(porcentaje, 140))
        
        return round(porcentaje, 2)
    
    def _generar_trea(self, porcentaje_devolucion: float, periodo: int) -> float:
        """
        Genera la TREA (Tasa de Rendimiento Efectiva Anual) basada en el porcentaje de devolución
        Fórmula: ((devolucion_total / aporte_total) ^ (1/periodo) - 1) * 100
        """
        # Convertir el porcentaje de devolución total a tasa anual
        tasa_total = (porcentaje_devolucion / 100)
        trea = (pow(tasa_total, 1/periodo) - 1) * 100
        
        # Ajuste por periodo (periodos más largos tienen TREA ligeramente mejor)
        ajuste_periodo = 1.0 + (periodo - 4) * 0.02
        trea = trea * ajuste_periodo
        
        return round(max(1.0, min(trea, 10.0)), 2)  # Entre 1.0% y 10% anual
    
    def _generar_tabla_devolucion(self, porcentaje_devolucion: float, periodo_pago: int) -> str:
        """
        Genera la tabla de devolución siguiendo la estructura requerida
        [60, 70, 70, ..., 70, porcentaje_final]
        """
        tabla = []
        
        for i in range(periodo_pago):
            if i == 0:
                # Primer elemento siempre es 60
                tabla.append(60)
            elif i == periodo_pago - 1:
                # Último elemento es el porcentaje de devolución
                tabla.append(porcentaje_devolucion)
            else:
                # Elementos intermedios son 70
                tabla.append(70)
        
        return json.dumps(tabla)
    
    def _calcular_campos_adicionales(
        self,
        porcentaje_devolucion: float,
        trea: float,
        prima: float,
        periodo_pago: int
    ) -> Dict[str, str]:
        """
        Calcula todos los campos necesarios para la cotización
        """
        # Aporte total = prima * 12 meses * periodo_pago
        aporte_total = prima * 12 * periodo_pago
        
        # Devolución total = aporte_total * (porcentaje_devolucion / 100)
        devolucion_total = aporte_total * (porcentaje_devolucion / 100)
        
        # Ganancia total = devolucion_total - aporte_total
        ganancia_total = devolucion_total - aporte_total
        
        # Rentabilidad = aporte_total - ganancia_total
        rentabilidad = aporte_total - ganancia_total
        
        return {
            "porcentaje_devolucion": str(round(porcentaje_devolucion, 2)),
            "trea": str(round(trea, 2)),
            "aporte_total": str(round(aporte_total, 2)),
            "ganancia_total": str(round(ganancia_total, 2)),
            "devolucion_total": str(round(devolucion_total, 2)),
            "rentabilidad": str(round(rentabilidad, 2))
        }
    
    def _cargar_periodos_config(self) -> List[Dict]:
        """Carga la configuración de periodos desde el archivo JSON"""
        with open(PERIODOS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _obtener_periodos_para_prima(self, prima: float) -> List[int]:
        """Obtiene los periodos disponibles para una prima específica"""
        config = self._cargar_periodos_config()
        
        for item in config:
            if prima in item["primas"]:
                return item["periodos"]
        
        return []
    
    def crear(self, cotizacion_data: CotizacionCreate) -> CotizacionResponse:
        """Crear una nueva cotización individual"""
        global contador_id
        
        # Generar porcentaje de devolución
        porcentaje_devolucion = self._generar_porcentaje_devolucion(
            periodo=cotizacion_data.parametros.periodo_pago,
            prima=cotizacion_data.parametros.prima,
            edad=cotizacion_data.parametros.edad_actuarial,
            sexo=cotizacion_data.parametros.sexo
        )
        
        # Generar TREA
        trea = self._generar_trea(porcentaje_devolucion, cotizacion_data.parametros.periodo_pago)
        
        # Generar tabla de devolución
        tabla_devolucion = self._generar_tabla_devolucion(
            porcentaje_devolucion=porcentaje_devolucion,
            periodo_pago=cotizacion_data.parametros.periodo_pago
        )
        
        # Calcular campos adicionales
        aporte_total = cotizacion_data.parametros.prima * 12 * cotizacion_data.parametros.periodo_pago
        devolucion_total = aporte_total * (porcentaje_devolucion / 100)
        
        # Crear la cotización
        nueva_cotizacion = CotizacionResponse(
            id=contador_id,
            producto=cotizacion_data.producto,
            parametros=cotizacion_data.parametros,
            fecha_creacion=datetime.now(),
            porcentaje_devolucion=porcentaje_devolucion / 100,  # Convertir a decimal
            tasa_implicita=trea / 100,  # Convertir a decimal
            suma_asegurada=aporte_total,
            devolucion=devolucion_total,
            prima_anual=cotizacion_data.parametros.prima * 12,
            tabla_devolucion=tabla_devolucion
        )
        
        cotizaciones_db.append(nueva_cotizacion)
        contador_id += 1
        
        return nueva_cotizacion
    
    def crear_cotizacion_coleccion(
        self,
        request: CotizacionColeccionRequest,
        generar_imagen: bool = True,
        usar_cache: bool = True
    ) -> CotizacionColeccionResponse:
        """
        Crea cotizaciones para todos los periodos disponibles de una prima específica
        """
        global _colecciones_cache
        
        # Verificar cache primero
        if usar_cache:
            cache_key = _generar_cache_key_coleccion(request.parametros.edad_actuarial, request.parametros.sexo, request.parametros.prima)
            if cache_key in _colecciones_cache:
                print(f"[CACHE COLECCIÓN] Encontrado: prima={request.parametros.prima}, edad={request.parametros.edad_actuarial}, sexo={request.parametros.sexo}")
                return _colecciones_cache[cache_key]
        
        # Obtener periodos disponibles para la prima
        periodos_disponibles = self._obtener_periodos_para_prima(request.parametros.prima)
        
        if not periodos_disponibles:
            return CotizacionColeccionResponse(
                prima=request.parametros.prima,
                periodos_disponibles=[],
                cotizaciones=[],
                total_cotizaciones=0,
                imagen_base64=None
            )
        
        # Generar cotizaciones para cada periodo
        cotizaciones = []
        
        for periodo in periodos_disponibles:
            # Generar porcentaje de devolución (incremental con el periodo)
            porcentaje_devolucion = self._generar_porcentaje_devolucion(
                periodo=periodo,
                prima=request.parametros.prima,
                edad=request.parametros.edad_actuarial,
                sexo=request.parametros.sexo
            )
            
            # Generar TREA
            trea = self._generar_trea(porcentaje_devolucion, periodo)
            
            # Calcular campos
            campos = self._calcular_campos_adicionales(
                porcentaje_devolucion=porcentaje_devolucion,
                trea=trea,
                prima=request.parametros.prima,
                periodo_pago=periodo
            )
            
            # Generar tabla de devolución
            tabla_devolucion = self._generar_tabla_devolucion(
                porcentaje_devolucion=porcentaje_devolucion,
                periodo_pago=periodo
            )
            
            # Crear detalle de cotización
            cotizacion_detalle = CotizacionDetalle(
                porcentaje_devolucion=campos["porcentaje_devolucion"],
                trea=campos["trea"],
                aporte_total=campos["aporte_total"],
                ganancia_total=campos["ganancia_total"],
                devolucion_total=campos["devolucion_total"],
                rentabilidad=campos["rentabilidad"],
                tabla_devolucion=tabla_devolucion
            )
            
            cotizaciones.append(CotizacionPorPeriodo(
                periodo=periodo,
                cotizacion=cotizacion_detalle
            ))
        
        # Generar imagen si se solicita
        imagen_base64 = None
        if generar_imagen and cotizaciones:
            try:
                from app.services.image_service import ImageService
                image_service = ImageService()
                
                data = {
                    "prima": request.parametros.prima,
                    "periodos_disponibles": periodos_disponibles,
                    "cotizaciones": [
                        {
                            "periodo": cot.periodo,
                            "cotizacion": cot.cotizacion.model_dump()
                        }
                        for cot in cotizaciones
                    ]
                }
                
                _, imagen_url = image_service.generar_grafico_cotizacion(
                    data=data,
                    nombre_archivo=f"cotizacion_prima{int(request.parametros.prima)}_edad{request.parametros.edad_actuarial}_{request.parametros.sexo}",
                    subir_temporal=True
                )
            except Exception as e:
                import traceback
                print(f"[ERROR] No se pudo generar la imagen: {str(e)}")
                traceback.print_exc()
        
        response = CotizacionColeccionResponse(
            prima=request.parametros.prima,
            periodos_disponibles=periodos_disponibles,
            cotizaciones=cotizaciones,
            total_cotizaciones=len(cotizaciones),
            imagen_base64=imagen_url  # Ahora contiene la URL temporal
        )
        
        # Guardar en cache
        if usar_cache:
            cache_key = _generar_cache_key_coleccion(request.parametros.edad_actuarial, request.parametros.sexo, request.parametros.prima)
            _colecciones_cache[cache_key] = response
            print(f"[CACHE COLECCIÓN] Guardado: prima={request.parametros.prima}, edad={request.parametros.edad_actuarial}, sexo={request.parametros.sexo}")
        
        return response
    
    def limpiar_cache_colecciones(self) -> int:
        """Limpia el cache de colecciones"""
        global _colecciones_cache
        cantidad = len(_colecciones_cache)
        _colecciones_cache.clear()
        print(f"[CACHE COLECCIÓN] Cache limpiado: {cantidad} elementos")
        return cantidad
    
    def obtener_estadisticas_cache(self) -> Dict:
        """Obtiene estadísticas del cache"""
        return {
            "cache_colecciones": len(_colecciones_cache)
        }

