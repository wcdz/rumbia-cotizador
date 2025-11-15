#!/bin/bash

# Script de deployment directo a Cloud Run usando gcloud CLI
# Sin necesidad de Cloud Build

set -e

PROJECT_ID="is-geniaton-ifs-2025-g3"
SERVICE_NAME="rumbia-cotizador"
REGION="us-central1"

echo "=== Deployment a Cloud Run con gcloud CLI ==="
echo "Proyecto: $PROJECT_ID"
echo "Servicio: $SERVICE_NAME"
echo "Región: $REGION"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI no está instalado"
    echo "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar proyecto
echo "Configurando proyecto..."
gcloud config set project $PROJECT_ID

# Desplegar directamente desde el código fuente
echo ""
echo "Desplegando a Cloud Run (esto construirá la imagen automáticamente)..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

echo ""
echo "=== Deployment completado ==="
echo ""
echo "Para ver la URL del servicio:"
echo "gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)'"
echo ""
echo "Para ver los logs:"
echo "gcloud run services logs read $SERVICE_NAME --region $REGION"

