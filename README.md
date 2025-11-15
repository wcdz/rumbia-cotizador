# RumbIA Cotizador API

API REST desarrollada con FastAPI para el sistema de cotizaciones RumbIA.

## 🚀 Características

- API RESTful con FastAPI
- Documentación interactiva automática (Swagger/OpenAPI)
- Validación de datos con Pydantic
- Estructura modular y escalable
- Manejo de CORS configurado

## 📋 Requisitos

- Python 3.8 o superior
- **Microsoft Excel instalado** (xlwings requiere Excel para funcionar)
- Windows (xlwings funciona mejor en Windows)

## 🔧 Instalación

1. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
```

2. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🏃 Ejecución

Para ejecutar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación

Una vez que el servidor esté corriendo, puedes acceder a:

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 🛣️ Endpoints

### Cotizaciones

#### `POST /api/v1/cotizaciones` - Crear cotización individual

Crea una nueva cotización y calcula el porcentaje de devolución.

**Ejemplo de Request:**
```json
{
    "producto": "RUMBO",
    "parametros": {
        "edad_actuarial": 18,
        "sexo": "M",
        "prima": 380,
        "periodo_pago": 5
    }
}
```

**Ejemplo de Response:**
```json
{
    "id": 1,
    "producto": "RUMBO",
    "parametros": {
        "edad_actuarial": 18,
        "sexo": "M",
        "prima": 380.0,
        "periodo_pago": 5
    },
    "fecha_creacion": "2024-01-15T10:30:00",
    "porcentaje_devolucion": 111.34,
    "tasa_implicita": 3.45,
    "tabla_devolucion": "[60, 70, 70, 70, 111.34]"
}
```

#### `POST /api/v1/cotizaciones/coleccion` - Crear cotizaciones por colección

Genera cotizaciones para todos los periodos disponibles de una prima específica.

**Ejemplo de Request:**
```json
{
    "producto": "RUMBO",
    "prima": 300,
    "edad_actuarial": 18,
    "sexo": "M"
}
```

**Ejemplo de Response:**
```json
{
    "prima": 300.0,
    "periodos_disponibles": [5, 6, 7],
    "cotizaciones": [
        {
            "periodo": 5,
            "cotizacion": {
                "porcentaje_devolucion": "103.52",
                "trea": "1.36",
                "aporte_total": "18000.0",
                "ganancia_total": "634.45",
                "devolucion_total": "18634.45",
                "rentabilidad": "17365.55",
                "tabla_devolucion": "[60, 70, 70, 70, 103.52]"
            }
        }
    ],
    "total_cotizaciones": 3
}
```

#### `POST /api/v1/cotizaciones/generar-imagen` - Generar imagen de cotización

Genera una imagen (JPEG) con gráfico y tabla de cotizaciones. La imagen se guarda en la carpeta `db/`.

**Ejemplo de Request:**
```json
{
    "prima": 300,
    "edad_actuarial": 18,
    "sexo": "M",
    "nombre_archivo": "cotizacion_cliente_123"
}
```

**Ejemplo de Response:**
```json
{
    "ruta_archivo": "C:\\path\\to\\db\\cotizacion_prima300_edad18_M_20241115_143022.jpg",
    "nombre_archivo": "cotizacion_prima300_edad18_M_20241115_143022.jpg",
    "mensaje": "Imagen generada exitosamente: cotizacion_prima300_edad18_M_20241115_143022.jpg"
}
```

**Nota:** El endpoint abre el archivo Excel en `assets/`, configura los parámetros, ejecuta el cálculo y retorna el porcentaje de devolución calculado.

## 📁 Estructura del Proyecto

```
rumbia-cotizador/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Aplicación principal FastAPI
│   ├── routers/                   # Endpoints de la API
│   │   ├── __init__.py
│   │   └── cotizaciones.py
│   ├── schemas/                   # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── cotizacion.py
│   └── services/                  # Lógica de negocio
│       ├── __init__.py
│       ├── cotizacion_service.py
│       └── image_service.py       # Servicio de generación de imágenes
├── assets/                        # Archivos de recursos
│   ├── configuracion_combinatorias/
│   │   └── periodos_cotizacion.json
│   └── macro_tecnica/
│       └── Rumbo_Modelo_produccion_2024 (version 1).xlsb.xlsm
├── db/                            # Carpeta para imágenes generadas
├── ejemplo_generar_imagen.py      # Script de ejemplo
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Este archivo
```

## ⚠️ Notas Importantes

- **xlwings requiere Microsoft Excel instalado** en el sistema
- El archivo Excel debe estar en la ruta `assets/Rumbo_Modelo_produccion_2024 (version 1).xlsb.xlsm`
- La hoja de trabajo debe llamarse `Parametros_Supuestos`
- El servicio abre Excel en modo invisible, configura los parámetros y ejecuta el cálculo
- Asegúrate de que el archivo Excel no esté abierto en otro proceso cuando uses la API
- Las imágenes generadas se guardan automáticamente en la carpeta `db/`

## 🎨 Servicio de Generación de Imágenes

El servicio de imágenes (`ImageService`) permite generar gráficos visuales de las cotizaciones:

### Características:
- **Gráfico de evolución**: Muestra la evolución del porcentaje de devolución por periodo
- **Tabla resumen**: Incluye información detallada de cada cotización (debajo del gráfico)
- **Formato JPEG**: Alta calidad (300 DPI) para impresión o presentación
- **Diseño moderno**: Colores profesionales y fácil lectura

### Uso desde Python:

```python
from app.services.image_service import ImageService

# Crear servicio
image_service = ImageService()

# Generar imagen
ruta = image_service.generar_grafico_desde_endpoint(
    prima=300.0,
    edad_actuarial=18,
    sexo="M"
)

print(f"Imagen guardada en: {ruta}")
```

### Uso desde API:

```bash
curl -X POST "http://localhost:8000/api/v1/cotizaciones/generar-imagen" \
  -H "Content-Type: application/json" \
  -d '{
    "prima": 300,
    "edad_actuarial": 18,
    "sexo": "M"
  }'
```

### Script de ejemplo:

Ejecuta el script de ejemplo incluido:

```bash
python ejemplo_generar_imagen.py
```

## 🔄 Próximos Pasos

- [ ] Integrar base de datos (PostgreSQL, MySQL, etc.)
- [ ] Agregar autenticación y autorización
- [ ] Implementar tests unitarios
- [ ] Agregar logging más detallado
- [ ] Configurar variables de entorno para rutas de archivos
- [ ] Manejar mejor los errores de Excel
- [ ] Agregar endpoint para descargar imágenes generadas

