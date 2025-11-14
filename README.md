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

- `POST /api/v1/cotizaciones` - Crear una nueva cotización y calcular porcentaje de devolución

#### Ejemplo de Request:
```json
{
    "producto": "RUMBO",
    "parametros": {
        "edad_actuarial": 18,
        "sexo": "M",
        "prima": 380
    }
}
```

#### Ejemplo de Response:
```json
{
    "id": 1,
    "producto": "RUMBO",
    "parametros": {
        "edad_actuarial": 18,
        "sexo": "M",
        "prima": 380.0
    },
    "fecha_creacion": "2024-01-15T10:30:00",
    "porcentaje_devolucion": 111.34
}
```

**Nota:** El endpoint abre el archivo Excel en `assets/`, configura los parámetros, ejecuta el cálculo y retorna el porcentaje de devolución calculado.

## 📁 Estructura del Proyecto

```
rumbia-cotizador/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── routers/             # Endpoints de la API
│   │   ├── __init__.py
│   │   └── cotizaciones.py
│   ├── schemas/             # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── cotizacion.py
│   └── services/            # Lógica de negocio
│       ├── __init__.py
│       └── cotizacion_service.py
├── assets/                  # Archivos de recursos
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## ⚠️ Notas Importantes

- **xlwings requiere Microsoft Excel instalado** en el sistema
- El archivo Excel debe estar en la ruta `assets/Rumbo_Modelo_produccion_2024 (version 1).xlsb.xlsm`
- La hoja de trabajo debe llamarse `Parametros_Supuestos`
- El servicio abre Excel en modo invisible, configura los parámetros y ejecuta el cálculo
- Asegúrate de que el archivo Excel no esté abierto en otro proceso cuando uses la API

## 🔄 Próximos Pasos

- [ ] Integrar base de datos (PostgreSQL, MySQL, etc.)
- [ ] Agregar autenticación y autorización
- [ ] Implementar tests unitarios
- [ ] Agregar logging más detallado
- [ ] Configurar variables de entorno para rutas de archivos
- [ ] Manejar mejor los errores de Excel

