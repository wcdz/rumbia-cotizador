# Instrucciones de Deployment a Cloud Run

## Prerequisitos

1. Tener instalado Google Cloud SDK (gcloud CLI)
   - Descargar: https://cloud.google.com/sdk/docs/install
2. Tener configurado el proyecto: `is-geniaton-ifs-2025-g3`
3. (Opcional) Tener Docker instalado para builds locales

## 🚀 Inicio Rápido

### Paso 1: Configurar gcloud (solo la primera vez)

```bash
# Ejecutar script de configuración
bash gcloud-setup.sh
```

O manualmente:

```bash
gcloud auth login
gcloud config set project is-geniaton-ifs-2025-g3
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### Paso 2: Desplegar

```bash
# Método más simple (RECOMENDADO)
bash deploy-cloudrun.sh
```

¡Listo! El servicio se desplegará automáticamente.

---

## Opciones de Deployment

### Opción 1: Deploy Directo con gcloud (RECOMENDADO - Más Rápido)

Cloud Build construye la imagen automáticamente en la nube:

```bash
bash deploy-cloudrun.sh
```

O el comando directo:

```bash
gcloud run deploy rumbia-cotizador \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars LIBREOFFICE_HEADLESS=1
```

**Ventajas:**
- No requiere Docker instalado localmente
- Construcción en la nube (más rápido en conexiones lentas)
- Automático y simple

### Opción 2: Deploy con Docker Local

Construye la imagen localmente y la sube:

```bash
bash deploy-with-docker.sh
```

**Ventajas:**
- Control total sobre la construcción
- Puedes probar la imagen localmente antes de desplegar
- Útil para debugging

### Opción 3: Deploy con Cloud Build (CI/CD)

Para pipelines de CI/CD automáticos:

```bash
gcloud builds submit --config=cloudbuild.yaml
```

---

## 🧪 Probar Localmente (antes de desplegar)

```bash
bash test_local.sh
```

Esto construye y ejecuta el contenedor localmente en http://localhost:8080

## 🔍 Verificar el Deployment

### Obtener URL del servicio

```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)'
```

### Probar el servicio

```bash
# Health check
SERVICE_URL=$(gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)')

curl $SERVICE_URL/health
curl $SERVICE_URL/

# Ver documentación interactiva
echo "API Docs: $SERVICE_URL/docs"
```

## 📊 Monitoreo y Logs

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

### Ver solo errores

```bash
gcloud run services logs read rumbia-cotizador \
  --region us-central1 \
  --log-filter='severity>=ERROR'
```

## 🔧 Gestión del Servicio

### Ver información del servicio

```bash
gcloud run services describe rumbia-cotizador --region us-central1
```

### Actualizar configuración

```bash
# Actualizar recursos
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4

# Actualizar variables de entorno
gcloud run services update rumbia-cotizador \
  --region us-central1 \
  --set-env-vars NUEVA_VAR=valor
```

### Ver revisiones (versiones)

```bash
gcloud run revisions list --service rumbia-cotizador --region us-central1
```

### Rollback a versión anterior

```bash
# Listar revisiones
gcloud run revisions list --service rumbia-cotizador --region us-central1

# Cambiar tráfico
gcloud run services update-traffic rumbia-cotizador \
  --region us-central1 \
  --to-revisions REVISION-NAME=100
```

## Consideraciones Importantes

### LibreOffice vs Excel

El proyecto originalmente usa `xlwings` que requiere Microsoft Excel. En Cloud Run (Linux) esto no es posible, por lo que se usa LibreOffice Calc.

**IMPORTANTE**: Las macros de Excel (VBA) NO son 100% compatibles con LibreOffice. Si el archivo Excel contiene macros complejas, pueden no funcionar correctamente.

#### Alternativas si las macros no funcionan:

1. **Portar la lógica a Python**: Extraer la lógica de las macros y reimplementarla en Python
2. **Simplificar el Excel**: Remover las macros y dejar solo fórmulas
3. **Pre-calcular valores**: Si el rango de valores es limitado, pre-calcular todas las combinaciones

### Recursos

El deployment usa:
- 2GB de memoria
- 2 vCPUs
- Timeout de 300 segundos (5 minutos)
- Max 10 instancias concurrentes

Ajusta estos valores según sea necesario en `cloudbuild.yaml` o en el comando de deployment.

### Costo

Cloud Run cobra por:
- Requests procesados
- Tiempo de CPU usado
- Memoria usada
- Bandwidth de salida

Con min-instances=0, no hay costo cuando no hay tráfico.

## Actualizar el Servicio

Para actualizar el código desplegado, simplemente vuelve a ejecutar el deployment con el mismo comando. Cloud Run hará un despliegue sin downtime.

## Eliminar el Servicio

```bash
gcloud run services delete rumbia-cotizador \
  --region=us-central1 \
  --project=is-geniaton-ifs-2025-g3
```

