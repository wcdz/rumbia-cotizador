"""
Script de ejemplo para generar imágenes de cotizaciones

Este script muestra cómo usar el ImageService para generar gráficos
de cotizaciones directamente desde Python.
"""

from app.services.image_service import ImageService
from app.services.cotizacion_service import CotizacionService
from app.schemas.cotizacion import CotizacionColeccionRequest


def ejemplo_basico():
    """Ejemplo básico: Generar imagen para una prima específica"""
    print("=" * 60)
    print("EJEMPLO 1: Generar imagen para prima de 300")
    print("=" * 60)
    
    # Crear servicio de imágenes
    image_service = ImageService()
    
    # Parámetros de ejemplo
    prima = 300.0
    edad_actuarial = 18
    sexo = "M"
    
    # Generar imagen
    ruta_archivo, _ = image_service.generar_grafico_desde_endpoint(
        prima=prima,
        edad_actuarial=edad_actuarial,
        sexo=sexo,
        retornar_base64=False
    )
    
    print(f"✓ Imagen generada exitosamente!")
    print(f"  Ruta: {ruta_archivo}")
    print()


def ejemplo_con_datos_personalizados():
    """Ejemplo avanzado: Generar imagen con datos personalizados"""
    print("=" * 60)
    print("EJEMPLO 2: Generar imagen con datos personalizados")
    print("=" * 60)
    
    # Crear servicios
    cotizacion_service = CotizacionService()
    image_service = ImageService()
    
    # Obtener datos de cotización
    request = CotizacionColeccionRequest(
        producto="RUMBO",
        prima=380.0,
        edad_actuarial=25,
        sexo="F"
    )
    
    response = cotizacion_service.crear_cotizacion_coleccion(request)
    
    print(f"Periodos disponibles: {response.periodos_disponibles}")
    print(f"Total de cotizaciones: {response.total_cotizaciones}")
    print()
    
    # Convertir a diccionario
    data = response.model_dump()
    
    # Generar imagen con nombre personalizado
    ruta_archivo, _ = image_service.generar_grafico_cotizacion(
        data=data,
        nombre_archivo="cotizacion_personalizada",
        retornar_base64=False
    )
    
    print(f"✓ Imagen generada exitosamente!")
    print(f"  Ruta: {ruta_archivo}")
    print()


def ejemplo_multiples_primas():
    """Ejemplo: Generar imágenes para múltiples primas"""
    print("=" * 60)
    print("EJEMPLO 3: Generar imágenes para múltiples primas")
    print("=" * 60)
    
    image_service = ImageService()
    
    # Lista de primas a procesar
    primas = [300, 400, 500]
    edad_actuarial = 30
    sexo = "M"
    
    for prima in primas:
        print(f"\nGenerando imagen para prima: {prima}")
        
        try:
            ruta_archivo, _ = image_service.generar_grafico_desde_endpoint(
                prima=float(prima),
                edad_actuarial=edad_actuarial,
                sexo=sexo,
                retornar_base64=False
            )
            print(f"  ✓ Generada: {ruta_archivo}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print("\n✓ Proceso completado!")


if __name__ == "__main__":
    print("\n🎨 EJEMPLOS DE GENERACIÓN DE IMÁGENES DE COTIZACIONES\n")
    
    try:
        # Ejecutar ejemplos
        ejemplo_basico()
        ejemplo_con_datos_personalizados()
        ejemplo_multiples_primas()
        
        print("=" * 60)
        print("✓ Todos los ejemplos ejecutados exitosamente")
        print("  Las imágenes se guardaron en la carpeta 'db/'")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error al ejecutar ejemplos: {str(e)}")
        import traceback
        traceback.print_exc()

