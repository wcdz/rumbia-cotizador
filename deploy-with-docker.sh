#!/bin/bash

# Script de deployment usando Docker + GCP CLI
# Construye la imagen localmente y la sube a Artifact Registry

set -e

PROJECT_ID="is-geniaton-ifs-2025-g3"
SERVICE_NAME="rumbia-cotizador"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=== Deployment con Docker + gcloud CLI ==="
echo "Proyecto: $PROJECT_ID"
echo "Servicio: $SERVICE_NAME"
echo "Región: $REGION"
echo "Imagen: $IMAGE_NAME"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI no está instalado"
    exit 1
fi

# Verificar que docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "Error: Docker no está instalado"
    exit 1
fi

# Configurar proyecto
echo "Configurando proyecto..."
gcloud config set project $PROJECT_ID

# Configurar Docker para GCR
echo "Configurando Docker para Google Container Registry..."
gcloud auth configure-docker

# Construir imagen
echo ""
echo "Construyendo imagen Docker..."
docker build -t $IMAGE_NAME:latest .

# Subir imagen
echo ""
echo "Subiendo imagen a Container Registry..."
docker push $IMAGE_NAME:latest

# Desplegar a Cloud Run
echo ""
echo "Desplegando a Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars LIBREOFFICE_HEADLESS=1

echo ""
echo "=== Deployment completado ==="
echo ""

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
echo "URL del servicio: $SERVICE_URL"
echo ""
echo "Prueba el servicio:"
echo "curl $SERVICE_URL/health"
echo ""
echo "Documentación API:"
echo "$SERVICE_URL/docs"

