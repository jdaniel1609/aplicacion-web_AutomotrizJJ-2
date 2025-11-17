# ==============================================================================
# Dockerfile para Backend - Automotriz JJ
# Python 3.11 Slim + FastAPI + SQLite/Azure SQL Database
# ==============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Automotriz JJ"
LABEL description="Backend FastAPI con soporte para SQLite y Azure SQL Database"
LABEL version="1.0"

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema necesarias para Azure SQL (ODBC)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Herramientas básicas
    curl \
    gnupg \
    apt-transport-https \
    # Dependencias para ODBC
    unixodbc \
    unixodbc-dev \
    # Limpieza
    && rm -rf /var/lib/apt/lists/*

# Instalar ODBC Driver 18 en Debian 12 (Trixie)
RUN curl https://packages.microsoft.com/keys/microsoft.asc \
      -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
      > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*


# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY /app ./app

# Crear directorio para SQLite database (si se usa)
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto (se pueden sobrescribir en docker-compose o docker run)
ENV DB_TYPE=sqlite \
    SECRET_KEY=change-this-secret-key-in-production \
    ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]