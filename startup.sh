#!/bin/bash

# Script de inicio para Cloud Run

echo "=== Iniciando RumbIA Cotizador ==="

# Crear directorio para imágenes
mkdir -p /app/db

echo "✓ Directorios creados"

# Iniciar la aplicación
echo "=== Iniciando servidor FastAPI ==="
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1

