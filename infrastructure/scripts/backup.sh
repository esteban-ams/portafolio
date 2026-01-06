#!/bin/bash
# =============================================================================
# Script de Backup
# =============================================================================
# Realiza backup de:
# - Base de datos PostgreSQL
# - Volumenes de Docker (configuraciones)
# - Certificados SSL
#
# Uso: ./backup.sh
# Programar con cron: 0 2 * * * /opt/apps/infrastructure/scripts/backup.sh
# =============================================================================

set -euo pipefail

# Configuracion
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Colores
GREEN='\033[0;32m'
NC='\033[0m'
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

log_info "Iniciando backup - $DATE"

# Crear directorio de backup
mkdir -p "$BACKUP_DIR/$DATE"

# -----------------------------------------------------------------------------
# Backup de PostgreSQL
# -----------------------------------------------------------------------------
log_info "Backup de PostgreSQL..."

docker exec postgres pg_dumpall -U admin > "$BACKUP_DIR/$DATE/postgres_all.sql"
gzip "$BACKUP_DIR/$DATE/postgres_all.sql"

log_info "PostgreSQL backup completado"

# -----------------------------------------------------------------------------
# Backup de volumenes de Docker
# -----------------------------------------------------------------------------
log_info "Backup de volumenes..."

# Certificados de Traefik
docker run --rm \
    -v traefik-certificates:/source:ro \
    -v "$BACKUP_DIR/$DATE":/backup \
    alpine tar czf /backup/traefik-certs.tar.gz -C /source .

# Datos de Uptime Kuma
docker run --rm \
    -v uptime-kuma-data:/source:ro \
    -v "$BACKUP_DIR/$DATE":/backup \
    alpine tar czf /backup/uptime-kuma.tar.gz -C /source .

log_info "Volumenes backup completado"

# -----------------------------------------------------------------------------
# Backup de archivos de configuracion
# -----------------------------------------------------------------------------
log_info "Backup de configuracion..."

tar czf "$BACKUP_DIR/$DATE/config.tar.gz" \
    -C /opt/apps \
    infrastructure/docker-compose.yml \
    infrastructure/traefik \
    infrastructure/.env 2>/dev/null || true

log_info "Configuracion backup completado"

# -----------------------------------------------------------------------------
# Limpiar backups antiguos
# -----------------------------------------------------------------------------
log_info "Limpiando backups antiguos (> $RETENTION_DAYS dias)..."

find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
log_info "Backup completado: $BACKUP_DIR/$DATE ($BACKUP_SIZE)"

# Listar backups existentes
log_info "Backups disponibles:"
ls -la "$BACKUP_DIR"
