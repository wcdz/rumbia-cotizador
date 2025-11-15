# 🚀 Guía Rápida de Deployment

## Para desplegar a Cloud Run (3 pasos)

### 1️⃣ Configurar (solo la primera vez)

```bash
bash gcloud-setup.sh
```

### 2️⃣ Desplegar

```bash
bash deploy-cloudrun.sh
```

### 3️⃣ Verificar

El script te mostrará la URL del servicio. También puedes obtenerla con:

```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)'
```

---

## 📚 Más información

- **DEPLOYMENT.md** - Guía completa de deployment con todas las opciones
- **gcloud-commands.md** - Todos los comandos útiles de gcloud para Cloud Run

---

## 🆘 Comandos útiles

### Ver logs
```bash
gcloud run services logs tail rumbia-cotizador --region us-central1
```

### Ver URL
```bash
gcloud run services describe rumbia-cotizador \
  --region us-central1 \
  --format='value(status.url)'
```

### Actualizar servicio
```bash
# Volver a ejecutar
bash deploy-cloudrun.sh
```

### Eliminar servicio
```bash
gcloud run services delete rumbia-cotizador --region us-central1
```

---

## 🐛 Solución de problemas

### "gcloud: command not found"
Instala Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### "Permission denied"
Verifica que estás autenticado:
```bash
gcloud auth login
```

### "Service already exists"
Esto es normal, el comando update actualizará el servicio existente.

### Error al construir
Revisa los logs:
```bash
gcloud builds list --limit 5
gcloud builds log [BUILD_ID]
```

---

## 💡 Scripts disponibles

- `gcloud-setup.sh` - Configuración inicial (primera vez)
- `deploy-cloudrun.sh` - Deploy directo (recomendado)
- `deploy-with-docker.sh` - Deploy con Docker local
- `test_local.sh` - Probar localmente antes de desplegar

---

## ⚙️ Configuración del proyecto

- **Proyecto GCP**: is-geniaton-ifs-2025-g3
- **Servicio**: rumbia-cotizador
- **Región**: us-central1
- **Memoria**: 2GB
- **CPU**: 2 vCPUs
- **Timeout**: 300 segundos

