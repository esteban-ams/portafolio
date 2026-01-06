#!/bin/bash
# =============================================================================
# Script de Sincronizacion y Despliegue Multi-proyecto
# =============================================================================
# Sincroniza todos los repositorios locales al servidor y ejecuta el deploy
#
# Uso: ./sync-and-deploy.sh
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURACION - EDITAR ESTOS VALORES
# =============================================================================
SERVER_IP="64.23.242.78"
SERVER_USER="root"
SSH_KEY="$HOME/.ssh/id_ed25519"

# Rutas locales de los proyectos
LOCAL_PORTFOLIO="/Users/estebanmartinezsoto/Development/git_repos/portafolio"
LOCAL_KOMERCIA="/Users/estebanmartinezsoto/Development/erp-market-django"
LOCAL_METALURGICA="/Users/estebanmartinezsoto/Development/metalurgica-spa"

# Rutas en el servidor
REMOTE_BASE="/opt/apps"
REMOTE_INFRA="/opt/infrastructure"

# =============================================================================
# COLORES Y FUNCIONES DE LOG
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}==>${NC} $1"; }

# =============================================================================
# VERIFICACIONES INICIALES
# =============================================================================
log_step "Verificando requisitos..."

# Verificar SSH key existe
if [[ ! -f "$SSH_KEY" ]]; then
    log_error "SSH key no encontrada: $SSH_KEY"
    exit 1
fi

# Verificar conexion al servidor
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "echo 'OK'" &>/dev/null; then
    log_error "No se puede conectar al servidor $SERVER_IP"
    log_warn "Asegurate de que:"
    log_warn "  1. El servidor esta encendido"
    log_warn "  2. Tu SSH key esta autorizada"
    log_warn "  3. El firewall permite SSH (puerto 22)"
    exit 1
fi

log_info "Conexion SSH verificada"

# =============================================================================
# FUNCION DE SINCRONIZACION
# =============================================================================
sync_project() {
    local name="$1"
    local local_path="$2"
    local remote_path="$3"

    log_step "Sincronizando $name..."

    if [[ ! -d "$local_path" ]]; then
        log_error "Directorio local no existe: $local_path"
        return 1
    fi

    # Crear directorio remoto si no existe
    ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "mkdir -p $remote_path"

    # Sincronizar con rsync (excluir archivos innecesarios)
    rsync -avz --delete \
        --exclude '.git' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.env' \
        --exclude 'venv' \
        --exclude 'node_modules' \
        --exclude '.DS_Store' \
        --exclude '*.sqlite3' \
        --exclude 'db.sqlite3' \
        --exclude '.claude' \
        --exclude 'media/*' \
        --exclude 'staticfiles/*' \
        -e "ssh -i $SSH_KEY" \
        "$local_path/" "$SERVER_USER@$SERVER_IP:$remote_path/"

    log_info "$name sincronizado"
}

# =============================================================================
# SINCRONIZACION DE PROYECTOS
# =============================================================================
log_step "Iniciando sincronizacion de proyectos..."

# Crear estructura de directorios en el servidor
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "mkdir -p $REMOTE_BASE $REMOTE_INFRA"

# Sincronizar cada proyecto
sync_project "Portfolio" "$LOCAL_PORTFOLIO" "$REMOTE_BASE/portfolio"
sync_project "Komercia" "$LOCAL_KOMERCIA" "$REMOTE_BASE/komercia"
sync_project "Metalurgica" "$LOCAL_METALURGICA" "$REMOTE_BASE/metalurgica-spa"

# Sincronizar infraestructura
sync_project "Infrastructure" "$LOCAL_PORTFOLIO/infrastructure" "$REMOTE_INFRA"

# =============================================================================
# CONFIGURAR .ENV EN EL SERVIDOR (si no existe)
# =============================================================================
log_step "Verificando archivo .env en el servidor..."

ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" bash << 'REMOTE_SCRIPT'
cd /opt/infrastructure

if [[ ! -f .env ]]; then
    echo "Creando archivo .env desde template..."
    if [[ -f .env.example ]]; then
        cp .env.example .env
        echo "IMPORTANTE: Edita /opt/infrastructure/.env con tus credenciales antes de desplegar"
    else
        cat > .env << 'EOF'
# =============================================================================
# Variables de Entorno - Produccion
# =============================================================================

# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=CAMBIA_ESTE_PASSWORD_SEGURO
POSTGRES_DB=main

# Traefik Dashboard Auth (genera con: htpasswd -nb admin TU_PASSWORD)
TRAEFIK_DASHBOARD_AUTH=admin:$apr1$xyz123$HASH_AQUI

# Komercia (Django)
KOMERCIA_SECRET_KEY=GENERA_UN_SECRET_KEY_DJANGO_SEGURO

# Portfolio (opcional)
RESEND_API_KEY=
CONTACT_EMAIL=

EOF
        echo "Archivo .env creado. EDITA LOS VALORES antes de continuar."
    fi
fi
REMOTE_SCRIPT

# =============================================================================
# EJECUTAR SETUP DEL SERVIDOR (si es primera vez)
# =============================================================================
log_step "Verificando si Docker esta instalado..."

DOCKER_INSTALLED=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "command -v docker &>/dev/null && echo 'yes' || echo 'no'")

if [[ "$DOCKER_INSTALLED" == "no" ]]; then
    log_warn "Docker no esta instalado. Ejecutando setup inicial..."
    ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "bash /opt/infrastructure/scripts/setup-droplet.sh"
    log_info "Setup completado. El servidor puede necesitar reinicio."
    log_warn "Ejecuta este script nuevamente despues del reinicio."
    exit 0
fi

log_info "Docker instalado"

# =============================================================================
# DESPLEGAR SERVICIOS
# =============================================================================
log_step "Desplegando servicios con Docker Compose..."

ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" bash << 'REMOTE_DEPLOY'
cd /opt/infrastructure

# Crear red de Traefik si no existe
docker network create traefik-public 2>/dev/null || true

# Verificar que .env tiene valores configurados
if grep -q "CAMBIA_ESTE_PASSWORD" .env; then
    echo "ERROR: Debes editar /opt/infrastructure/.env con valores reales"
    echo "Ejecuta: ssh root@164.92.100.196 'nano /opt/infrastructure/.env'"
    exit 1
fi

# Build y deploy
docker compose pull
docker compose build
docker compose up -d

# Esperar a que los servicios arranquen
sleep 10

# Mostrar estado
echo ""
echo "=== ESTADO DE SERVICIOS ==="
docker compose ps

# Ejecutar migraciones de Django para Komercia
echo ""
echo "=== EJECUTANDO MIGRACIONES DE KOMERCIA ==="
docker compose exec -T komercia python src/manage.py migrate --noinput || echo "Migraciones pendientes (servicio puede estar iniciando)"

# Recolectar static files de Django
docker compose exec -T komercia python src/manage.py collectstatic --noinput || echo "Collectstatic pendiente"

REMOTE_DEPLOY

# =============================================================================
# RESUMEN FINAL
# =============================================================================
log_step "Despliegue completado!"

echo ""
echo "=========================================="
echo "         RESUMEN DEL DESPLIEGUE          "
echo "=========================================="
echo ""
echo "Servidor: $SERVER_IP"
echo ""
echo "Servicios desplegados:"
echo "  - Portfolio:    https://esteban-ams.cl"
echo "                  https://portafolio.esteban-ams.cl"
echo "  - Komercia:     https://komercia.esteban-ams.cl"
echo "  - Metalurgica:  https://metalurgica.esteban-ams.cl"
echo "  - Status:       https://status.esteban-ams.cl"
echo "  - Traefik:      https://traefik.esteban-ams.cl"
echo ""
echo "Comandos utiles:"
echo "  Ver logs:       ssh root@$SERVER_IP 'cd /opt/infrastructure && docker compose logs -f'"
echo "  Reiniciar:      ssh root@$SERVER_IP 'cd /opt/infrastructure && docker compose restart'"
echo "  Estado:         ssh root@$SERVER_IP 'cd /opt/infrastructure && docker compose ps'"
echo ""
echo "IMPORTANTE: Asegurate de configurar los DNS en NIC.cl"
echo "=========================================="
