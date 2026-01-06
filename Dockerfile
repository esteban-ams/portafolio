# =============================================================================
# Dockerfile para Portfolio FastHTML
# Optimizado para produccion con multi-stage build
# =============================================================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias de compilacion
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Crear virtualenv e instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Argumentos de build
ARG APP_USER=appuser
ARG APP_UID=1000

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=5001

WORKDIR /app

# Crear usuario no-root para seguridad
RUN groupadd --gid $APP_UID $APP_USER && \
    useradd --uid $APP_UID --gid $APP_USER --shell /bin/bash $APP_USER

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar codigo de la aplicacion
COPY --chown=$APP_USER:$APP_USER . .

# Cambiar a usuario no-root
USER $APP_USER

# Puerto expuesto (debe coincidir con PORT env)
EXPOSE 5001

# Health check para Traefik y monitoreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/')" || exit 1

# Comando de inicio usando gunicorn para produccion
CMD ["gunicorn", "main:app", \
     "--bind", "0.0.0.0:5001", \
     "--workers", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance"]
