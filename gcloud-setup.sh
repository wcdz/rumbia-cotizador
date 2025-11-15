#!/bin/bash

# Script para configurar gcloud CLI para el proyecto

PROJECT_ID="is-geniaton-ifs-2025-g3"
REGION="us-central1"

echo "=== Configuración de gcloud CLI ==="
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI no está instalado"
    echo ""
    echo "Instala desde:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✓ gcloud CLI encontrado"
echo ""

# Login (si es necesario)
echo "Autenticando con Google Cloud..."
gcloud auth login

# Configurar proyecto
echo ""
echo "Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Configurar región por defecto
echo ""
echo "Configurando región por defecto: $REGION"
gcloud config set run/region $REGION

# Habilitar APIs necesarias
echo ""
echo "Habilitando APIs necesarias..."
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com

# Configurar Docker para GCR
echo ""
echo "Configurando Docker para Google Container Registry..."
gcloud auth configure-docker

echo ""
echo "=== Configuración completada ==="
echo ""
echo "Proyecto actual: $(gcloud config get-value project)"
echo "Región Cloud Run: $(gcloud config get-value run/region)"
echo ""
echo "Para desplegar la aplicación, ejecuta:"
echo "  ./deploy-cloudrun.sh    (más rápido, construye en la nube)"
echo "  ./deploy-with-docker.sh (construye localmente con Docker)"

