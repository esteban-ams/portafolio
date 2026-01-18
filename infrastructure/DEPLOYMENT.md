# Arquitectura de Despliegue - esteban-ams.cl

Documentación completa de la infraestructura multi-proyecto desplegada en DigitalOcean.

## Resumen

| Componente | Tecnología | URL |
|------------|------------|-----|
| Portfolio | FastHTML | https://esteban-ams.cl, https://portafolio.esteban-ams.cl |
| Komercia Landing | FastHTML | https://komercia.esteban-ams.cl |
| Komercia Cloud | Django | https://app.komercia.esteban-ams.cl |
| Metalurgica SPA | FastHTML | https://metalurgica.esteban-ams.cl |
| Uptime Kuma | Node.js | https://status.esteban-ams.cl |
| Traefik Dashboard | - | https://traefik.esteban-ams.cl |

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DigitalOcean Droplet                                │
│                        Ubuntu 22.04 / 2GB RAM                                │
│                          IP: 64.23.242.78                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         TRAEFIK v2.11                                │   │
│  │                   (Reverse Proxy + SSL Manager)                      │   │
│  │                                                                      │   │
│  │   :80 ──────────────────────────────────> :443 (redirect HTTPS)     │   │
│  │   :443 ─────────────────────────────────> Servicios internos        │   │
│  │                                                                      │   │
│  │   Certificados: Let's Encrypt (HTTP-01 Challenge)                   │   │
│  │   Red: traefik-public                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         │                          │                          │            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐      │
│  │  PORTFOLIO  │           │  KOMERCIA   │           │ KOMERCIA    │      │
│  │  FastHTML   │           │  LANDING    │           │ CLOUD       │      │
│  │  :5001      │           │  FastHTML   │           │ Django      │      │
│  │             │           │  :5003      │           │ :8000       │      │
│  └─────────────┘           └─────────────┘           └─────────────┘      │
│                                                             │              │
│  ┌─────────────┐           ┌─────────────┐                 │              │
│  │ METALURGICA │           │ UPTIME KUMA │                 │              │
│  │  FastHTML   │           │  Node.js    │                 │              │
│  │  :5002      │           │  :3001      │                 │              │
│  └─────────────┘           └─────────────┘                 │              │
│                                    │                        │              │
│                                    │   ┌────────────────────┘              │
│                                    │   │                                   │
│                                    ▼   ▼                                   │
│                            ┌─────────────────┐                             │
│                            │   POSTGRESQL    │                             │
│                            │   v16-alpine    │                             │
│                            │   (Red interna) │                             │
│                            └─────────────────┘                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Estructura de Archivos

```
/opt/apps/                          # Directorio principal en servidor
├── infrastructure/                 # Este directorio
│   ├── docker-compose.yml         # Definición de todos los servicios
│   ├── .env                       # Variables de entorno (NO en git)
│   ├── .env.example               # Template de variables
│   ├── traefik/
│   │   ├── traefik.yml            # Configuración estática de Traefik
│   │   └── dynamic/
│   │       └── security-headers.yml
│   └── scripts/
│       ├── setup-droplet.sh       # Setup inicial del servidor
│       ├── deploy.sh              # Despliegue de servicios
│       ├── backup.sh              # Backup de datos
│       ├── sync-and-deploy.sh     # Sync + deploy desde local
│       └── init-databases.sql     # Inicialización de DBs
├── portfolio/                      # Código del portfolio (este repo)
├── komercia-landing/              # Landing page de Komercia
├── komercia/                      # Django ERP (Komercia Cloud)
└── metalurgica-spa/               # Landing Metalurgica
```

## Servicios

### 1. Traefik (Reverse Proxy)

**Imagen:** `traefik:v2.11`

Funciones:
- Reverse proxy para todos los servicios
- Terminación SSL con Let's Encrypt
- Redirección automática HTTP → HTTPS
- Descubrimiento automático de servicios via Docker labels

**Configuración:**
- Puerto 80: Redirección a HTTPS
- Puerto 443: Tráfico principal
- Dashboard: https://traefik.esteban-ams.cl (protegido con Basic Auth)

### 2. Portfolio (FastHTML)

**Imagen:** Build local desde `Dockerfile`
**Puerto interno:** 5001

Dominios:
- https://esteban-ams.cl
- https://www.esteban-ams.cl
- https://portafolio.esteban-ams.cl

### 3. Komercia Landing (FastHTML)

**Imagen:** Build local desde `Dockerfile`
**Puerto interno:** 5003

Dominio: https://komercia.esteban-ams.cl

Rutas:
- `/` - Landing principal
- `/pos` - Página de Komercia POS
- `/cloud` - Página de Komercia Cloud

### 4. Komercia Cloud (Django)

**Imagen:** Build local desde `Dockerfile`
**Puerto interno:** 8000

Dominio: https://app.komercia.esteban-ams.cl

**Base de datos:** PostgreSQL compartido (DB: `komercia`)

### 5. Metalurgica SPA (FastHTML)

**Imagen:** Build local desde `Dockerfile`
**Puerto interno:** 5002

Dominio: https://metalurgica.esteban-ams.cl

### 6. Uptime Kuma (Monitoreo)

**Imagen:** `louislam/uptime-kuma:1`
**Puerto interno:** 3001

Dominio: https://status.esteban-ams.cl

### 7. PostgreSQL

**Imagen:** `postgres:16-alpine`
**Puerto interno:** 5432 (no expuesto)

- Solo accesible desde red interna
- Volumen persistente: `postgres-data`
- Bases de datos: `main`, `komercia`

## Redes Docker

| Red | Propósito |
|-----|-----------|
| `traefik-public` | Comunicación con Traefik (externa) |
| `internal` | Comunicación con PostgreSQL (interna) |

## Volúmenes

| Volumen | Uso |
|---------|-----|
| `traefik-certificates` | Certificados SSL Let's Encrypt |
| `postgres-data` | Datos de PostgreSQL |
| `uptime-kuma-data` | Configuración de Uptime Kuma |
| `komercia-media` | Archivos subidos de Komercia |
| `komercia-static` | Archivos estáticos de Django |

## Despliegue

### Setup Inicial del Servidor

```bash
# 1. En el Droplet nuevo (como root)
bash setup-droplet.sh

# 2. Crear red de Docker
docker network create traefik-public

# 3. Copiar archivos
scp -r infrastructure/* root@64.23.242.78:/opt/apps/infrastructure/

# 4. Configurar variables de entorno
cp .env.example .env
vim .env  # Completar valores

# 5. Desplegar
./scripts/deploy.sh
```

### Despliegue de Cambios

#### Opción 1: Desde local (recomendado)

```bash
# Sync y deploy de un servicio específico
./scripts/sync-and-deploy.sh portfolio

# O manualmente:
rsync -avz --exclude '__pycache__' --exclude '.git' \
  /ruta/local/proyecto/ root@64.23.242.78:/opt/apps/proyecto/

ssh root@64.23.242.78 "cd /opt/apps/infrastructure && \
  docker compose build proyecto && \
  docker compose up -d proyecto"
```

#### Opción 2: Desde el servidor

```bash
ssh root@64.23.242.78
cd /opt/apps/infrastructure
./scripts/deploy.sh [servicio]
```

### Comandos Útiles

```bash
# Ver estado de servicios
docker compose ps

# Ver logs de un servicio
docker compose logs -f portfolio

# Reiniciar un servicio
docker compose restart portfolio

# Rebuild completo
docker compose build --no-cache portfolio
docker compose up -d portfolio

# Acceder a PostgreSQL
docker exec -it postgres psql -U admin -d komercia

# Ver certificados SSL
docker exec traefik cat /certificates/acme.json | jq
```

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
# Traefik Dashboard (htpasswd -nb admin PASSWORD)
TRAEFIK_DASHBOARD_AUTH=admin:$apr1$...

# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=password_seguro_32_chars
POSTGRES_DB=main

# Portfolio/Komercia Landing
RESEND_API_KEY=re_xxxxxxxxxxxxx
CONTACT_EMAIL=contacto@esteban-ams.cl

# Komercia Cloud (Django)
KOMERCIA_SECRET_KEY=django-secret-key-50-chars
```

## DNS

Configuración en NIC.cl (o proveedor DNS):

| Tipo | Nombre | Valor |
|------|--------|-------|
| A | @ | 64.23.242.78 |
| A | * | 64.23.242.78 |

El wildcard `*.esteban-ams.cl` permite agregar nuevos subdominios sin configuración DNS adicional.

## Monitoreo

### Uptime Kuma

Acceder a https://status.esteban-ams.cl para:
- Configurar monitores de uptime
- Ver historial de disponibilidad
- Configurar alertas

### Health Checks

Cada servicio tiene healthcheck configurado:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:PORT/')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

Traefik solo enruta tráfico a contenedores healthy.

## Seguridad

### Firewall (UFW)

```
Puertos abiertos:
- 22 (SSH)
- 80 (HTTP → redirige a HTTPS)
- 443 (HTTPS)
```

### Fail2Ban

Protección contra ataques de fuerza bruta en SSH:
- Ban time: 1 hora
- Max retries: 3

### SSL/TLS

- Certificados automáticos via Let's Encrypt
- HTTP-01 Challenge
- Renovación automática

### Headers de Seguridad

Configurados en `traefik/dynamic/security-headers.yml`:
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Content-Security-Policy

## Backup

```bash
# Backup de PostgreSQL
./scripts/backup.sh

# Los backups se guardan en /opt/backups/
```

## Troubleshooting

### Servicio no responde

```bash
# Verificar estado
docker compose ps

# Ver logs
docker compose logs servicio

# Verificar healthcheck
docker inspect servicio --format='{{json .State.Health}}' | jq
```

### Certificado SSL no funciona

```bash
# Ver logs de Traefik
docker compose logs traefik | grep -i "acme\|certificate"

# Verificar que DNS apunta correctamente
dig +short subdominio.esteban-ams.cl
```

### Container unhealthy

```bash
# Verificar que la app responde internamente
docker exec servicio python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:PORT/').status)"
```

## Agregar Nuevo Proyecto

1. Crear `Dockerfile` en el proyecto
2. Agregar servicio en `docker-compose.yml`:

```yaml
nuevo-proyecto:
  build:
    context: /opt/apps/nuevo-proyecto
    dockerfile: Dockerfile
  image: nuevo-proyecto:latest
  container_name: nuevo-proyecto
  restart: unless-stopped
  networks:
    - traefik-public
  environment:
    - PORT=500X
    - DEBUG=false
    - TZ=America/Santiago
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:500X/')"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.nuevo-proyecto.rule=Host(`nuevo.esteban-ams.cl`)"
    - "traefik.http.routers.nuevo-proyecto.entrypoints=websecure"
    - "traefik.http.routers.nuevo-proyecto.tls.certresolver=letsencrypt"
    - "traefik.http.services.nuevo-proyecto.loadbalancer.server.port=500X"
    - "traefik.docker.network=traefik-public"
```

3. Sync código al servidor
4. Ejecutar `./scripts/deploy.sh nuevo-proyecto`

## Contacto

- **Dominio:** esteban-ams.cl
- **IP Droplet:** 64.23.242.78
- **Región:** NYC1 (DigitalOcean)
