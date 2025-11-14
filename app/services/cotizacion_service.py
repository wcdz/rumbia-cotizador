import os
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import hashlib
import xlwings as xw
from app.schemas.cotizacion import CotizacionCreate, CotizacionResponse

# Simulación de base de datos en memoria (en producción usar una BD real)
cotizaciones_db: List[CotizacionResponse] = []
contador_id = 1

# Cache para la macro del botón (se busca una vez y se reutiliza)
_boton_macro_cache: Optional[str] = None

# Cache para resultados de cotizaciones (key: hash de parámetros, value: tupla de resultados)
_cotizaciones_cache: Dict[str, Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]] = {}


def _generar_cache_key(edad_actuarial: int, sexo: str, prima: float) -> str:
    """Genera una clave única para el cache basada en los parámetros"""
    # Crear un hash de los parámetros para usar como clave
    params_str = f"{edad_actuarial}_{sexo}_{prima}"
    return hashlib.md5(params_str.encode()).hexdigest()

# Ruta al archivo Excel
EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                          "assets", "macro_tecnica", "Rumbo_Modelo_produccion_2024 (version 1).xlsb.xlsm")
EXCEL_SHEET = "Parametros_Supuestos"


class CotizacionService:
    """Servicio para manejar la lógica de negocio de cotizaciones"""
    
    def _calcular_cotizacion_excel(self, edad_actuarial: int, sexo: str, prima: float, usar_cache: bool = True) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Abre el Excel, configura los parámetros, ejecuta el cálculo y obtiene el resultado
        Usa cache para evitar recalcular si los parámetros son los mismos
        
        Args:
            edad_actuarial: Edad de contratación
            sexo: Sexo del cliente (M o F)
            prima: Prima calculada mensual
            usar_cache: Si True, usa cache cuando está disponible
            
        Returns:
            Tupla con (porcentaje_devolucion, tasa_implicita, suma_asegurada, devolucion, prima_anual) o (None, None, None, None, None) si hay error
        """
        global _cotizaciones_cache
        
        # Verificar cache primero
        if usar_cache:
            cache_key = _generar_cache_key(edad_actuarial, sexo, prima)
            if cache_key in _cotizaciones_cache:
                print(f"[CACHE] Resultado encontrado en cache para parámetros: edad={edad_actuarial}, sexo={sexo}, prima={prima}")
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
                    cache_key = _generar_cache_key(edad_actuarial, sexo, prima)
                    _cotizaciones_cache[cache_key] = resultado
                    print(f"[CACHE] Resultado guardado en cache para parámetros: edad={edad_actuarial}, sexo={sexo}, prima={prima}")
                
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
            prima=cotizacion_data.parametros.prima
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
            prima_anual=prima_anual
        )
        
        cotizaciones_db.append(nueva_cotizacion)
        contador_id += 1
        
        return nueva_cotizacion

