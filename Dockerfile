# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Instalar solo dependencias necesarias para matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    libpng16-16 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/db

# Exponer el puerto
EXPOSE 8080

# Copiar script de inicio
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Comando para iniciar la aplicación
CMD ["/app/startup.sh"]

