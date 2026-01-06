#!/bin/bash
# =============================================================================
# Script de Setup Inicial del Droplet
# =============================================================================
# Ejecutar como root en un Droplet Ubuntu 22.04/24.04 limpio
# Uso: curl -sSL URL_DEL_SCRIPT | bash
#      o: bash setup-droplet.sh
# =============================================================================

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   log_error "Este script debe ejecutarse como root"
   exit 1
fi

log_info "=== Iniciando setup del Droplet ==="

# -----------------------------------------------------------------------------
# 1. Actualizar sistema
# -----------------------------------------------------------------------------
log_info "Actualizando sistema..."
apt-get update && apt-get upgrade -y

# -----------------------------------------------------------------------------
# 2. Instalar paquetes esenciales
# -----------------------------------------------------------------------------
log_info "Instalando paquetes esenciales..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    htop \
    vim \
    ufw \
    fail2ban \
    unattended-upgrades

# -----------------------------------------------------------------------------
# 3. Instalar Docker
# -----------------------------------------------------------------------------
log_info "Instalando Docker..."

# Agregar clave GPG oficial de Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Agregar repositorio
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Habilitar Docker
systemctl enable docker
systemctl start docker

log_info "Docker instalado: $(docker --version)"

# -----------------------------------------------------------------------------
# 4. Crear usuario deploy (no-root)
# -----------------------------------------------------------------------------
log_info "Creando usuario 'deploy'..."

if ! id "deploy" &>/dev/null; then
    useradd -m -s /bin/bash -G docker deploy
    log_info "Usuario 'deploy' creado"
else
    log_warn "Usuario 'deploy' ya existe"
fi

# Agregar a grupo docker
usermod -aG docker deploy

# -----------------------------------------------------------------------------
# 5. Configurar Firewall (UFW)
# -----------------------------------------------------------------------------
log_info "Configurando firewall..."

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https

# Habilitar firewall (sin confirmacion)
echo "y" | ufw enable

log_info "Firewall configurado"

# -----------------------------------------------------------------------------
# 6. Configurar Fail2Ban
# -----------------------------------------------------------------------------
log_info "Configurando Fail2Ban..."

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

log_info "Fail2Ban configurado"

# -----------------------------------------------------------------------------
# 7. Crear estructura de directorios
# -----------------------------------------------------------------------------
log_info "Creando estructura de directorios..."

mkdir -p /opt/apps
mkdir -p /opt/traefik/{dynamic,logs}
mkdir -p /opt/backups

chown -R deploy:deploy /opt/apps
chown -R deploy:deploy /opt/traefik
chown -R deploy:deploy /opt/backups

# -----------------------------------------------------------------------------
# 8. Crear red de Docker para Traefik
# -----------------------------------------------------------------------------
log_info "Creando red Docker 'traefik-public'..."

docker network create traefik-public 2>/dev/null || log_warn "Red traefik-public ya existe"

# -----------------------------------------------------------------------------
# 9. Configurar actualizaciones automaticas de seguridad
# -----------------------------------------------------------------------------
log_info "Configurando actualizaciones automaticas..."

cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

# -----------------------------------------------------------------------------
# 10. Configurar swap (2GB para Droplet de 2GB RAM)
# -----------------------------------------------------------------------------
log_info "Configurando swap..."

if [[ ! -f /swapfile ]]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab

    # Optimizar swap
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' >> /etc/sysctl.conf

    log_info "Swap de 2GB configurado"
else
    log_warn "Swap ya existe"
fi

# -----------------------------------------------------------------------------
# Resumen final
# -----------------------------------------------------------------------------
echo ""
echo "=============================================="
log_info "SETUP COMPLETADO"
echo "=============================================="
echo ""
echo "Proximos pasos:"
echo "1. Configurar SSH keys para usuario 'deploy'"
echo "2. Copiar archivos de infraestructura a /opt/apps"
echo "3. Crear archivo .env con credenciales"
echo "4. Configurar DNS wildcard en NIC.cl"
echo "5. Ejecutar docker compose up -d"
echo ""
echo "Acceso al servidor:"
echo "  ssh deploy@$(curl -s ifconfig.me)"
echo ""
echo "=============================================="
