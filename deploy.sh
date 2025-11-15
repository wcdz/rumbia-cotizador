#!/bin/bash

# Script de deployment rápido - usa el método más simple
# Redirige a deploy-cloudrun.sh

echo "=== Deployment Rápido a Cloud Run ==="
echo ""
echo "Usando deployment directo desde código fuente..."
echo "Si prefieres construir con Docker primero, usa: ./deploy-with-docker.sh"
echo ""

# Ejecutar el script de deployment directo
bash deploy-cloudrun.sh

