#!/bin/bash
# =============================================================================
# Script de Despliegue
# =============================================================================
# Uso: ./deploy.sh [servicio]
# Ejemplo: ./deploy.sh portfolio
#          ./deploy.sh  (despliega todo)
# =============================================================================

set -euo pipefail

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Directorio de trabajo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"

cd "$INFRA_DIR"

# Verificar archivo .env
if [[ ! -f .env ]]; then
    log_warn "Archivo .env no encontrado. Creando desde template..."
    cp .env.example .env
    echo "Por favor, edita .env con tus credenciales y ejecuta de nuevo."
    exit 1
fi

# Cargar variables de entorno
set -a
source .env
set +a

# Servicio a desplegar (opcional)
SERVICE="${1:-}"

if [[ -n "$SERVICE" ]]; then
    log_info "Desplegando servicio: $SERVICE"

    # Rebuild y restart del servicio especifico
    docker compose build "$SERVICE"
    docker compose up -d "$SERVICE"

    log_info "Servicio $SERVICE desplegado"
else
    log_info "Desplegando toda la infraestructura..."

    # Pull de imagenes actualizadas
    docker compose pull

    # Build de imagenes locales
    docker compose build

    # Levantar servicios
    docker compose up -d

    log_info "Infraestructura desplegada"
fi

# Mostrar estado
echo ""
log_info "Estado de los servicios:"
docker compose ps

# Verificar logs de Traefik para errores
echo ""
log_info "Verificando Traefik..."
docker compose logs --tail=10 traefik | grep -E "(error|Error|ERROR)" || echo "Sin errores recientes en Traefik"

echo ""
log_info "Despliegue completado"
