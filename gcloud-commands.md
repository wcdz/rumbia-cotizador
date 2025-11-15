# Comandos útiles de gcloud para Cloud Run

## Configuración Inicial

### Instalar gcloud CLI
```bash
# Descargar desde: https://cloud.google.com/sdk/docs/install
# Después de instalar, inicializar:
gcloud init
```

### Configurar el proyecto
```bash
gcloud config set project is-geniaton-ifs-2025-g3
gcloud config set run/region us-central1
```

### Habilitar APIs necesarias
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Deployment

### Opción 1: Deploy directo desde código (RECOMENDADO)
```bash
# Cloud Build construye automáticamente la imagen
gcloud run deploy rumbia-cotizador \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars LIBREOFFICE_HEADLESS=1
```

### Opción 2: Deploy con Docker pre-construido
```bash
# 1. Construir imagen
docker build -t gcr.io/is-geniaton-ifs-2025-g3/rumbia-cotizador:latest .

# 2. Configurar Docker
gcloud auth configure-docker

# 3. Push imagen
docker push gcr.io/is-geniaton-ifs-2025-g3/rumbia-cotizador:latest

# 4. Deploy
gcloud run deploy rumbia-cotizador \
  --image gcr.io/is-geniaton-ifs-2025-g3/rumbia-cotizador:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Opción 3: Deploy con Cloud Build (desde GitHub/Cloud Source)
```bash
gcloud builds submit --config=cloudbuild.yaml
```

## Gestión del Servicio

### Ver información del servicio
```bash
gcloud run services describe rumbia-cotizador --region us-central1
```

### Obtener URL del servicio
```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)'
```

### Listar todos los servicios
```bash
gcloud run services list
```

### Ver revisiones (versiones)
```bash
gcloud run revisions list --service rumbia-cotizador --region us-central1
```

## Logs y Monitoreo

### Ver logs en tiempo real
```bash
gcloud run services logs tail rumbia-cotizador --region us-central1
```

### Ver logs históricos
```bash
gcloud run services logs read rumbia-cotizador \
  --region us-central1 \
  --limit 100
```

### Ver logs de una revisión específica
```bash
gcloud run revisions logs read [REVISION-NAME] --region us-central1
```

## Actualización del Servicio

### Actualizar variables de entorno
```bash
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --set-env-vars NUEVA_VAR=valor
```

### Actualizar recursos (memoria/CPU)
```bash
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4
```

### Actualizar timeout
```bash
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --timeout 600
```

### Actualizar escalado
```bash
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --max-instances 20 \
  --min-instances 1
```

## Tráfico y Revisiones

### Ver distribución de tráfico
```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.traffic)'
```

### Migrar tráfico entre revisiones
```bash
gcloud run services update-traffic rumbia-cotizador \
  --region us-central1 \
  --to-revisions REVISION-NEW=100
```

### Rollback a revisión anterior
```bash
# Listar revisiones
gcloud run revisions list --service rumbia-cotizador --region us-central1

# Cambiar tráfico a revisión anterior
gcloud run services update-traffic rumbia-cotizador \
  --region us-central1 \
  --to-revisions REVISION-OLD=100
```

## IAM y Permisos

### Hacer el servicio público (sin autenticación)
```bash
gcloud run services add-iam-policy-binding rumbia-cotizador \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Hacer el servicio privado (requiere autenticación)
```bash
gcloud run services remove-iam-policy-binding rumbia-cotizador \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Eliminación

### Eliminar el servicio
```bash
gcloud run services delete rumbia-cotizador --region us-central1
```

### Eliminar imágenes del Container Registry
```bash
# Listar imágenes
gcloud container images list --repository=gcr.io/is-geniaton-ifs-2025-g3

# Eliminar imagen específica
gcloud container images delete gcr.io/is-geniaton-ifs-2025-g3/rumbia-cotizador:latest
```

## Testing

### Hacer una request al servicio
```bash
# Health check
SERVICE_URL=$(gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)')

curl $SERVICE_URL/health
curl $SERVICE_URL/
```

### Ver documentación de la API
```bash
# Abrir en navegador
SERVICE_URL=$(gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)')

echo "Documentación: $SERVICE_URL/docs"
```

## Debugging

### Ver métricas
```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.conditions)'
```

### Ver detalles de errores
```bash
gcloud run services logs read rumbia-cotizador \
  --region us-central1 \
  --log-filter='severity>=ERROR'
```

### Conectar a instancia en ejecución (para debugging)
```bash
# No es posible SSH en Cloud Run, pero puedes ver logs en tiempo real
gcloud run services logs tail rumbia-cotizador \
  --region us-central1 \
  --format='value(textPayload)'
```

## Información de Costos

### Ver uso de recursos
```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='table(status.latestReadyRevisionName, status.traffic)'
```

### Configurar para minimizar costos
```bash
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 3 \
  --cpu 1 \
  --memory 1Gi \
  --timeout 60
```

## Scripts Útiles

### Script para deployment completo
```bash
#!/bin/bash
gcloud run deploy rumbia-cotizador \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Script para ver URL y hacer test
```bash
#!/bin/bash
URL=$(gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)')
echo "Servicio: $URL"
curl -f $URL/health && echo "✓ Servicio OK"
```

