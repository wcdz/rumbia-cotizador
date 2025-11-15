import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import cotizaciones

app = FastAPI(
    title="RumbIA Cotizador API",
    description="API para el sistema de cotizaciones RumbIA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio para imágenes si no existe
os.makedirs("db", exist_ok=True)

# Servir archivos estáticos (imágenes)
app.mount("/images", StaticFiles(directory="db"), name="images")

# Incluir routers
app.include_router(cotizaciones.router, prefix="/api/v1", tags=["cotizaciones"])


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de RumbIA Cotizador",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

