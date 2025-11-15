#!/bin/bash

# Script para probar localmente el deployment

echo "=== Prueba local del contenedor Docker ==="

# Construir imagen
echo "Construyendo imagen..."
docker build -t rumbia-cotizador-local:latest .

if [ $? -ne 0 ]; then
    echo "Error al construir la imagen"
    exit 1
fi

# Ejecutar contenedor
echo "Ejecutando contenedor..."
docker run -p 8080:8080 --rm \
  -e PORT=8080 \
  -e LIBREOFFICE_HEADLESS=1 \
  rumbia-cotizador-local:latest &

CONTAINER_PID=$!

# Esperar a que el servidor inicie
echo "Esperando a que el servidor inicie..."
sleep 5

# Probar el endpoint de health
echo "Probando endpoint de health..."
curl -f http://localhost:8080/health

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Servidor funcionando correctamente"
    echo "✓ Accede a http://localhost:8080/docs para ver la API"
    echo ""
    echo "Presiona Ctrl+C para detener el servidor"
    wait $CONTAINER_PID
else
    echo ""
    echo "✗ Error al conectar con el servidor"
    kill $CONTAINER_PID 2>/dev/null
    exit 1
fi

