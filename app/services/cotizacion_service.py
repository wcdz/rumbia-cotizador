import os
import json
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import hashlib
import xlwings as xw
from app.schemas.cotizacion import (
    CotizacionCreate, 
    CotizacionResponse,
    CotizacionColeccionRequest,
    CotizacionColeccionResponse,
    CotizacionPorPeriodo,
    CotizacionDetalle
)

# Simulación de base de datos en memoria (en producción usar una BD real)
cotizaciones_db: List[CotizacionResponse] = []
contador_id = 1

# Cache para la macro del botón (se busca una vez y se reutiliza)
_boton_macro_cache: Optional[str] = None

# Cache para resultados de cotizaciones (key: hash de parámetros, value: tupla de resultados)
_cotizaciones_cache: Dict[str, Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]] = {}

# Cache para colecciones de cotizaciones (key: hash de parámetros, value: CotizacionColeccionResponse)
_colecciones_cache: Dict[str, 'CotizacionColeccionResponse'] = {}


def _generar_cache_key(edad_actuarial: int, sexo: str, prima: float, periodo_pago: int) -> str:
    """Genera una clave única para el cache basada en los parámetros"""
    # Crear un hash de los parámetros para usar como clave
    params_str = f"{edad_actuarial}_{sexo}_{prima}_{periodo_pago}"
    return hashlib.md5(params_str.encode()).hexdigest()


def _generar_cache_key_coleccion(edad_actuarial: int, sexo: str, prima: float) -> str:
    """Genera una clave única para el cache de colecciones"""
    params_str = f"coleccion_{edad_actuarial}_{sexo}_{prima}"
    return hashlib.md5(params_str.encode()).hexdigest()

# Ruta al archivo Excel
EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                          "assets", "macro_tecnica", "Rumbo_Modelo_produccion_2024 (version 1).xlsb.xlsm")
EXCEL_SHEET = "Parametros_Supuestos"

# Ruta al archivo de configuración de periodos
PERIODOS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    "assets", "configuracion_combinatorias", "periodos_cotizacion.json")


class CotizacionService:
    """Servicio para manejar la lógica de negocio de cotizaciones"""
    
    def _generar_tabla_devolucion(self, porcentaje_devolucion: Optional[float], periodo_pago: int) -> Optional[str]:
        """
        Genera la tabla de devolución basada en el porcentaje de devolución y periodo de pago
        
        Args:
            porcentaje_devolucion: Porcentaje de devolución calculado
            periodo_pago: Periodo de pago
            
        Returns:
            String con el array de devolución en formato JSON o None si porcentaje_devolucion es None
        """
        if porcentaje_devolucion is None:
            return None
        
        tabla = []
        
        for i in range(periodo_pago):
            if i == 0:
                # Primer elemento siempre es 60
                tabla.append(60)
            elif i == periodo_pago - 1:
                # Último elemento es el porcentaje de devolución
                tabla.append(round(porcentaje_devolucion * 100, 2))
            else:
                # Elementos intermedios son 70
                tabla.append(70)
        
        # Convertir a string JSON
        return json.dumps(tabla)
    
    def _calcular_cotizacion_excel(self, edad_actuarial: int, sexo: str, prima: float, periodo_pago: int, usar_cache: bool = True) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Abre el Excel, configura los parámetros, ejecuta el cálculo y obtiene el resultado
        Usa cache para evitar recalcular si los parámetros son los mismos
        
        Args:
            edad_actuarial: Edad de contratación
            sexo: Sexo del cliente (M o F)
            prima: Prima calculada mensual
            periodo_pago: Periodo de pago
            usar_cache: Si True, usa cache cuando está disponible
            
        Returns:
            Tupla con (porcentaje_devolucion, tasa_implicita, suma_asegurada, devolucion, prima_anual) o (None, None, None, None, None) si hay error
        """
        global _cotizaciones_cache
        
        # Verificar cache primero
        if usar_cache:
            cache_key = _generar_cache_key(edad_actuarial, sexo, prima, periodo_pago)
            if cache_key in _cotizaciones_cache:
                print(f"[CACHE] Resultado encontrado en cache para parámetros: edad={edad_actuarial}, sexo={sexo}, prima={prima}, periodo_pago={periodo_pago}")
                return _cotizaciones_cache[cache_key]
        
        import time
        app = None
        try:
            # Abrir el libro de Excel (visible=False para que no se muestre)
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(EXCEL_PATH)
            ws = wb.sheets[EXCEL_SHEET]
            
            try:
                # Configurar los valores en las celdas
                ws.range("C8").value = periodo_pago  # Periodo de Pago
                ws.range("C9").value = periodo_pago  # Periodo de Pago (ambas celdas)
                ws.range("C15").value = edad_actuarial  # Edad de Contratación
                ws.range("C13").value = sexo  # Sexo
                ws.range("C22").value = prima  # Prima Calculada Mensual
                
                # Leer el valor inicial de C11 para comparar después
                valor_inicial = ws.range("C11").value
                
                # Buscar el botón "Ejecutar" usando cache
                global _boton_macro_cache
                button_found = False
                
                try:
                    # Usar cache si está disponible
                    if _boton_macro_cache:
                        try:
                            app.api.Run(_boton_macro_cache)
                            button_found = True
                        except:
                            # Si falla, limpiar cache y buscar de nuevo
                            _boton_macro_cache = None
                    
                    if not button_found:
                        # Buscar el botón con macro asociada
                        for shape in ws.shapes:
                            try:
                                if hasattr(shape.api, 'OnAction'):
                                    macro_name = shape.api.OnAction
                                    if macro_name:
                                        _boton_macro_cache = macro_name  # Guardar en cache
                                        app.api.Run(macro_name)
                                        button_found = True
                                        break
                            except:
                                continue
                    
                    if button_found:
                        # Esperar hasta que Excel termine de calcular
                        max_wait_time = 8  # Máximo 8 segundos
                        wait_interval = 0.05  # Verificar cada 0.05 segundos
                        elapsed_time = 0
                        
                        while elapsed_time < max_wait_time:
                            try:
                                # Verificar el estado de cálculo de Excel
                                calculation_state = app.api.CalculationState
                                # 0 = xlDone (terminado), -4135 = xlCalculating (calculando)
                                if calculation_state != -4135:  # Terminado
                                    # Verificar que el valor haya cambiado
                                    valor_actual = ws.range("C11").value
                                    if valor_actual != valor_inicial:
                                        # Valor cambió, esperar un poco más para asegurar estabilidad
                                        time.sleep(0.1)
                                        break
                                
                                time.sleep(wait_interval)
                                elapsed_time += wait_interval
                                
                            except:
                                time.sleep(wait_interval)
                                elapsed_time += wait_interval
                    else:
                        # Si no se encontró el botón, forzar cálculo manual
                        app.api.Calculate()
                        time.sleep(0.3)
                        
                except Exception as btn_error:
                    app.api.Calculate()
                    time.sleep(0.3)
                
                # Leer los resultados de las celdas
                porcentaje_devolucion = ws.range("C11").value
                tasa_implicita = ws.range("C21").value
                suma_asegurada = ws.range("C10").value
                devolucion = ws.range("C29").value
                prima_anual = ws.range("C30").value
                
                # Convertir a float si es necesario
                if porcentaje_devolucion is not None:
                    try:
                        porcentaje_devolucion = float(porcentaje_devolucion)
                    except:
                        pass
                
                if tasa_implicita is not None:
                    try:
                        tasa_implicita = float(tasa_implicita)
                    except:
                        pass
                
                if suma_asegurada is not None:
                    try:
                        suma_asegurada = float(suma_asegurada)
                    except:
                        pass
                
                if devolucion is not None:
                    try:
                        devolucion = float(devolucion)
                    except:
                        pass
                
                if prima_anual is not None:
                    try:
                        prima_anual = float(prima_anual)
                    except:
                        pass
                
                resultado = (porcentaje_devolucion, tasa_implicita, suma_asegurada, devolucion, prima_anual)
                
                # Guardar en cache si todos los valores son válidos
                if usar_cache and all(v is not None for v in resultado):
                    cache_key = _generar_cache_key(edad_actuarial, sexo, prima, periodo_pago)
                    _cotizaciones_cache[cache_key] = resultado
                    print(f"[CACHE] Resultado guardado en cache para parámetros: edad={edad_actuarial}, sexo={sexo}, prima={prima}, periodo_pago={periodo_pago}")
                
                return resultado
                
            finally:
                # Cerrar el libro sin guardar cambios
                try:
                    wb.close()
                except:
                    pass
                app.quit()
                
        except Exception as e:
            # En caso de error, intentar cerrar Excel si está abierto
            if app:
                try:
                    app.quit()
                except:
                    pass
            import traceback
            error_msg = f"[ERROR] Error al calcular cotización en Excel: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return None, None, None, None, None
    
    def crear(self, cotizacion_data: CotizacionCreate) -> CotizacionResponse:
        """Crear una nueva cotización y calcular el porcentaje de devolución y tasa implícita"""
        global contador_id
        
        # Calcular los valores usando Excel
        porcentaje_devolucion, tasa_implicita, suma_asegurada, devolucion, prima_anual = self._calcular_cotizacion_excel(
            edad_actuarial=cotizacion_data.parametros.edad_actuarial,
            sexo=cotizacion_data.parametros.sexo,
            prima=cotizacion_data.parametros.prima,
            periodo_pago=cotizacion_data.parametros.periodo_pago
        )
        
        # Generar la tabla de devolución
        tabla_devolucion = self._generar_tabla_devolucion(
            porcentaje_devolucion=porcentaje_devolucion,
            periodo_pago=cotizacion_data.parametros.periodo_pago
        )
        
        # Crear la cotización
        nueva_cotizacion = CotizacionResponse(
            id=contador_id,
            producto=cotizacion_data.producto,
            parametros=cotizacion_data.parametros,
            fecha_creacion=datetime.now(),
            porcentaje_devolucion=porcentaje_devolucion,
            tasa_implicita=tasa_implicita,
            suma_asegurada=suma_asegurada,
            devolucion=devolucion,
            prima_anual=prima_anual,
            tabla_devolucion=tabla_devolucion
        )
        
        cotizaciones_db.append(nueva_cotizacion)
        contador_id += 1
        
        return nueva_cotizacion
    
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
    
    def _calcular_campos_adicionales(
        self,
        porcentaje_devolucion: Optional[float],
        tasa_implicita: Optional[float],
        suma_asegurada: Optional[float],
        devolucion: Optional[float],
        prima_anual: Optional[float],
        prima: float,
        periodo_pago: int
    ) -> Dict[str, Optional[str]]:
        """
        Calcula campos adicionales para la cotización por colección
        
        Returns:
            Diccionario con todos los campos calculados en formato string
        """
        try:
            # Convertir porcentaje de devolución de decimal a porcentaje y redondear
            porcentaje_dev_str = str(round(porcentaje_devolucion * 100, 2)) if porcentaje_devolucion is not None else None
            
            # Tasa implícita (trea)
            trea_str = str(round(tasa_implicita * 100, 2)) if tasa_implicita is not None else None
            
            # Aporte total = prima * 12 meses * periodo_pago
            aporte_total = prima * 12 * periodo_pago
            aporte_total_str = str(round(aporte_total, 2))
            
            # Devolución total (ya viene calculada del Excel)
            devolucion_total_str = str(round(devolucion, 2)) if devolucion is not None else None
            
            # Ganancia total = devolucion_total - aporte_total
            if devolucion is not None:
                ganancia_total = devolucion - aporte_total
                ganancia_total_str = str(round(ganancia_total, 2))
            else:
                ganancia_total_str = None
            
            # Rentabilidad = aporte_total - ganancia_total
            if suma_asegurada is not None:
                rentabilidad = aporte_total - ganancia_total
                rentabilidad_str = str(round(rentabilidad, 2))
            else:
                rentabilidad_str = None
            
            return {
                "porcentaje_devolucion": porcentaje_dev_str,
                "trea": trea_str,
                "aporte_total": aporte_total_str,
                "ganancia_total": ganancia_total_str,
                "devolucion_total": devolucion_total_str,
                "rentabilidad": rentabilidad_str
            }
        except Exception as e:
            print(f"[ERROR] Error calculando campos adicionales: {str(e)}")
            return {
                "porcentaje_devolucion": None,
                "trea": None,
                "aporte_total": None,
                "ganancia_total": None,
                "devolucion_total": None,
                "rentabilidad": None
            }
    
    def crear_cotizacion_coleccion(self, request: CotizacionColeccionRequest, generar_imagen: bool = True, usar_cache: bool = True) -> CotizacionColeccionResponse:
        """
        Crea cotizaciones para todos los periodos disponibles de una prima específica
        """
        global _colecciones_cache
        
        # Verificar cache primero
        if usar_cache:
            cache_key = _generar_cache_key_coleccion(request.edad_actuarial, request.sexo, request.prima)
            if cache_key in _colecciones_cache:
                print(f"[CACHE COLECCIÓN] Resultado encontrado en cache para: prima={request.prima}, edad={request.edad_actuarial}, sexo={request.sexo}")
                return _colecciones_cache[cache_key]
        
        # Obtener periodos disponibles para la prima
        periodos_disponibles = self._obtener_periodos_para_prima(request.prima)
        
        if not periodos_disponibles:
            # Si no hay periodos configurados, retornar respuesta vacía
            return CotizacionColeccionResponse(
                prima=request.prima,
                periodos_disponibles=[],
                cotizaciones=[],
                total_cotizaciones=0,
                imagen_base64=None
            )
        
        # Generar cotizaciones para cada periodo
        cotizaciones = []
        
        for periodo in periodos_disponibles:
            # Calcular cotización usando Excel
            porcentaje_devolucion, tasa_implicita, suma_asegurada, devolucion, prima_anual = self._calcular_cotizacion_excel(
                edad_actuarial=request.edad_actuarial,
                sexo=request.sexo,
                prima=request.prima,
                periodo_pago=periodo
            )
            
            # Calcular campos adicionales
            campos = self._calcular_campos_adicionales(
                porcentaje_devolucion=porcentaje_devolucion,
                tasa_implicita=tasa_implicita,
                suma_asegurada=suma_asegurada,
                devolucion=devolucion,
                prima_anual=prima_anual,
                prima=request.prima,
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
            
            # Agregar a la lista
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
                
                # Crear data para la imagen
                data = {
                    "prima": request.prima,
                    "periodos_disponibles": periodos_disponibles,
                    "cotizaciones": [
                        {
                            "periodo": cot.periodo,
                            "cotizacion": cot.cotizacion.model_dump()
                        }
                        for cot in cotizaciones
                    ]
                }
                
                # Generar imagen con base64 directamente
                _, imagen_base64 = image_service.generar_grafico_cotizacion(
                    data=data,
                    nombre_archivo=f"cotizacion_prima{int(request.prima)}_edad{request.edad_actuarial}_{request.sexo}",
                    retornar_base64=True
                )
            except Exception as e:
                import traceback
                print(f"[ERROR] No se pudo generar la imagen: {str(e)}")
                traceback.print_exc()
        
        # Crear respuesta
        response = CotizacionColeccionResponse(
            prima=request.prima,
            periodos_disponibles=periodos_disponibles,
            cotizaciones=cotizaciones,
            total_cotizaciones=len(cotizaciones),
            imagen_base64=imagen_base64
        )
        
        # Guardar en cache
        if usar_cache:
            cache_key = _generar_cache_key_coleccion(request.edad_actuarial, request.sexo, request.prima)
            _colecciones_cache[cache_key] = response
            print(f"[CACHE COLECCIÓN] Resultado guardado en cache para: prima={request.prima}, edad={request.edad_actuarial}, sexo={request.sexo}")
        
        return response
    
    def limpiar_cache_colecciones(self) -> int:
        """Limpia el cache de colecciones y retorna el número de elementos eliminados"""
        global _colecciones_cache
        cantidad = len(_colecciones_cache)
        _colecciones_cache.clear()
        print(f"[CACHE COLECCIÓN] Cache limpiado: {cantidad} elementos eliminados")
        return cantidad
    
    def obtener_estadisticas_cache(self) -> Dict:
        """Obtiene estadísticas del cache"""
        return {
            "cache_cotizaciones": len(_cotizaciones_cache),
            "cache_colecciones": len(_colecciones_cache)
        }

