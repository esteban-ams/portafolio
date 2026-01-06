# Guia de Despliegue - Infraestructura Multi-proyecto

Esta guia detalla como migrar de DigitalOcean App Platform a un Droplet con Docker, Traefik y soporte para multiples proyectos.

## Arquitectura Final

```
                    Internet
                        |
                   [Firewall]
                        |
                    [Droplet]
                   2GB/1vCPU
                        |
            +-----------+-----------+
            |                       |
        [Traefik]              [Docker Network]
        Port 80/443            traefik-public
            |                       |
    +-------+-------+-------+-------+
    |       |       |       |       |
[Portfolio][Demo1][Status][Traefik]
            |               Dashboard
            |
      [PostgreSQL]
      (red interna)
```

## Costos Estimados

| Recurso | Costo Mensual |
|---------|---------------|
| Droplet 2GB/1vCPU | $12 USD |
| Dominio (.cl) | ~$10 USD/año |
| **Total Mensual** | **~$13 USD** |

Comparado con App Platform (~$5/app), esto permite hospedar multiples apps por el mismo precio.

---

## Paso 1: Crear el Droplet con doctl

### Prerequisitos

```bash
# Instalar doctl (macOS)
brew install doctl

# Autenticar con tu cuenta de DigitalOcean
doctl auth init
# Ingresa tu API token desde: https://cloud.digitalocean.com/account/api/tokens
```

### Crear SSH Key (si no tienes una)

```bash
# Generar clave SSH
ssh-keygen -t ed25519 -C "tu-email@esteban-ams.cl"

# Agregar la clave a DigitalOcean
doctl compute ssh-key create mi-clave-ssh \
  --public-key "$(cat ~/.ssh/id_ed25519.pub)"

# Obtener el ID de la clave (lo necesitaras)
doctl compute ssh-key list
```

### Crear el Droplet

```bash
# Listar regiones disponibles
doctl compute region list

# Listar imagenes disponibles
doctl compute image list --public | grep ubuntu

# Crear el Droplet
doctl compute droplet create servidor-esteban \
  --size s-1vcpu-2gb \
  --image ubuntu-24-04-x64 \
  --region nyc1 \
  --ssh-keys TU_SSH_KEY_ID \
  --enable-monitoring \
  --tag-names "produccion,web" \
  --wait

# Ver IP del Droplet
doctl compute droplet list --format Name,PublicIPv4
```

**Resultado esperado:**
```
Name               Public IPv4
servidor-esteban   123.456.789.10
```

Guarda esta IP, la necesitaras para configurar DNS.

---

## Paso 2: Configuracion DNS en NIC.cl

### Opcion A: DNS en NIC.cl (Recomendado)

Accede a tu panel en [NIC.cl](https://nic.cl) y configura:

| Tipo | Host | Valor | TTL |
|------|------|-------|-----|
| A | @ | 123.456.789.10 | 3600 |
| A | * | 123.456.789.10 | 3600 |
| CNAME | www | esteban-ams.cl. | 3600 |

El registro `*` (wildcard) redirige todos los subdominios al Droplet.

### Opcion B: DNS en DigitalOcean

```bash
# Agregar dominio a DigitalOcean
doctl compute domain create esteban-ams.cl

# Crear registros DNS
doctl compute domain records create esteban-ams.cl \
  --record-type A --record-name @ \
  --record-data 123.456.789.10 --record-ttl 3600

doctl compute domain records create esteban-ams.cl \
  --record-type A --record-name "*" \
  --record-data 123.456.789.10 --record-ttl 3600

doctl compute domain records create esteban-ams.cl \
  --record-type CNAME --record-name www \
  --record-data esteban-ams.cl. --record-ttl 3600

# Verificar registros
doctl compute domain records list esteban-ams.cl
```

Si usas esta opcion, actualiza los nameservers en NIC.cl a:
- ns1.digitalocean.com
- ns2.digitalocean.com
- ns3.digitalocean.com

### Verificar propagacion DNS

```bash
# Esperar unos minutos y verificar
dig esteban-ams.cl +short
dig portafolio.esteban-ams.cl +short
dig status.esteban-ams.cl +short
```

---

## Paso 3: Setup Inicial del Droplet

### Conectar al servidor

```bash
ssh root@123.456.789.10
```

### Ejecutar script de setup

```bash
# Opcion 1: Descargar y ejecutar
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/portafolio/main/infrastructure/scripts/setup-droplet.sh | bash

# Opcion 2: Copiar y ejecutar manualmente
# (copia el contenido de infrastructure/scripts/setup-droplet.sh)
```

El script automaticamente:
- Actualiza el sistema
- Instala Docker y Docker Compose
- Configura firewall (UFW)
- Configura Fail2Ban
- Crea usuario `deploy`
- Configura swap de 2GB
- Crea red Docker `traefik-public`

### Configurar acceso SSH para usuario deploy

```bash
# Como root, copiar SSH keys al usuario deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### Verificar acceso

```bash
# Desde tu maquina local
ssh deploy@123.456.789.10
```

---

## Paso 4: Desplegar Infraestructura

### Copiar archivos al servidor

```bash
# Desde tu maquina local, en el directorio del proyecto
rsync -avz --progress \
  infrastructure/ \
  deploy@123.456.789.10:/opt/apps/infrastructure/

# Copiar Dockerfile (necesario para build)
rsync -avz --progress \
  Dockerfile .dockerignore requirements.txt \
  main.py components/ pages/ data/ services/ static/ content/ \
  deploy@123.456.789.10:/opt/apps/portfolio/
```

### Conectar y configurar

```bash
ssh deploy@123.456.789.10
cd /opt/apps/infrastructure

# Crear archivo .env desde template
cp .env.example .env

# Editar con tus valores reales
nano .env
```

### Generar hash para Traefik Dashboard

```bash
# Instalar htpasswd si no existe
sudo apt-get install -y apache2-utils

# Generar hash (reemplaza TU_PASSWORD)
htpasswd -nb admin TU_PASSWORD_SEGURO
# Output: admin:$apr1$xyz123$abcdefghij...

# Copiar el output completo al .env en TRAEFIK_DASHBOARD_AUTH
```

### Actualizar email en traefik.yml

```bash
nano /opt/apps/infrastructure/traefik/traefik.yml
# Cambiar: email: "tu-email@esteban-ams.cl"
```

### Actualizar Dockerfile path

El docker-compose espera el Dockerfile en el directorio padre:

```bash
# Mover archivos del portfolio
mv /opt/apps/portfolio/* /opt/apps/
# O actualizar el context en docker-compose.yml
```

### Desplegar

```bash
cd /opt/apps/infrastructure

# Crear red si no existe
docker network create traefik-public 2>/dev/null || true

# Levantar infraestructura
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar estado
docker compose ps
```

---

## Paso 5: Verificacion

### Verificar servicios

```bash
# Estado de contenedores
docker ps

# Logs de Traefik
docker logs traefik --tail 50

# Logs del portfolio
docker logs portfolio --tail 50
```

### Verificar SSL

```bash
# Esperar 1-2 minutos para que Traefik obtenga certificados
curl -I https://portafolio.esteban-ams.cl
curl -I https://status.esteban-ams.cl
```

### URLs disponibles

| Servicio | URL |
|----------|-----|
| Portfolio | https://portafolio.esteban-ams.cl |
| Portfolio (dominio principal) | https://esteban-ams.cl |
| Uptime Kuma | https://status.esteban-ams.cl |
| Traefik Dashboard | https://traefik.esteban-ams.cl |

---

## Agregar Nuevos Proyectos

### Checklist Rapido

- [ ] Crear Dockerfile en el proyecto
- [ ] Agregar servicio en `infrastructure/docker-compose.yml`
- [ ] Agregar ruta local en `infrastructure/scripts/sync-and-deploy.sh`
- [ ] Crear registro DNS en DigitalOcean (si es nuevo subdominio)
- [ ] Sincronizar y desplegar

---

### Paso 1: Crear Dockerfile en tu proyecto

#### Para FastHTML (Python)

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
EXPOSE 5000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### Para Django

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

#### Para Node.js / Next.js

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["npm", "start"]
```

---

### Paso 2: Agregar servicio en docker-compose.yml

Edita `infrastructure/docker-compose.yml` y agrega tu nuevo servicio:

```yaml
  # ===========================================================================
  # AGENCYFLOW - Tu Nueva App
  # Dominio: agencyflow.esteban-ams.cl
  # ===========================================================================
  agencyflow:
    build:
      context: /opt/apps/agencyflow
      dockerfile: Dockerfile
    image: agencyflow:latest
    container_name: agencyflow
    restart: unless-stopped
    networks:
      - traefik-public
      # - internal  # Agregar si necesita acceso a PostgreSQL
    environment:
      - PORT=5000
      - DEBUG=false
      - TZ=America/Santiago
      # Agregar variables especificas de tu app
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.agencyflow.rule=Host(`agencyflow.esteban-ams.cl`)"
      - "traefik.http.routers.agencyflow.entrypoints=websecure"
      - "traefik.http.routers.agencyflow.tls.certresolver=letsencrypt"
      - "traefik.http.services.agencyflow.loadbalancer.server.port=5000"
      - "traefik.docker.network=traefik-public"
```

**Notas importantes:**
- Cambia `agencyflow` por el nombre de tu proyecto (en minusculas, sin espacios)
- El puerto debe coincidir con el EXPOSE del Dockerfile
- Si necesita base de datos, agrega `- internal` en networks y `depends_on: postgres`

---

### Paso 3: Agregar al script de sincronizacion

Edita `infrastructure/scripts/sync-and-deploy.sh`:

```bash
# Agregar ruta local (busca la seccion de rutas)
LOCAL_AGENCYFLOW="/Users/estebanmartinezsoto/Development/agencyflow"

# Agregar sincronizacion (busca donde se sincronizan los otros proyectos)
sync_project "AgencyFlow" "$LOCAL_AGENCYFLOW" "$REMOTE_BASE/agencyflow"
```

---

### Paso 4: Crear registro DNS (si es nuevo subdominio)

Ya tienes configurado un wildcard `*.esteban-ams.cl`, asi que cualquier subdominio nuevo funcionara automaticamente.

Si quieres verificar:
```bash
dig agencyflow.esteban-ams.cl +short
# Debe mostrar: 64.23.242.78
```

---

### Paso 5: Desplegar

```bash
# Opcion A: Desplegar todo
./infrastructure/scripts/sync-and-deploy.sh

# Opcion B: Solo el nuevo proyecto
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude 'node_modules' \
  ~/Development/agencyflow/ \
  root@64.23.242.78:/opt/apps/agencyflow/

ssh root@64.23.242.78 "cd /opt/infrastructure && docker compose up -d agencyflow"
```

---

### Paso 6: Verificar

```bash
# Estado del contenedor
ssh root@64.23.242.78 "cd /opt/infrastructure && docker compose ps agencyflow"

# Logs
ssh root@64.23.242.78 "docker logs agencyflow --tail 50"

# Probar HTTPS
curl -I https://agencyflow.esteban-ams.cl
```

---

### Ejemplo Completo: Agregar AgencyFlow

```bash
# 1. Crear Dockerfile en ~/Development/agencyflow/Dockerfile

# 2. Editar docker-compose.yml local
code ~/Development/git_repos/portafolio/infrastructure/docker-compose.yml

# 3. Editar sync-and-deploy.sh
code ~/Development/git_repos/portafolio/infrastructure/scripts/sync-and-deploy.sh

# 4. Sincronizar y desplegar
cd ~/Development/git_repos/portafolio
./infrastructure/scripts/sync-and-deploy.sh

# 5. Verificar
curl -I https://agencyflow.esteban-ams.cl
```

---

### Apps con Base de Datos

Si tu app necesita PostgreSQL:

1. Agrega la red `internal` al servicio:
```yaml
networks:
  - traefik-public
  - internal
```

2. Agrega dependencia:
```yaml
depends_on:
  postgres:
    condition: service_healthy
```

3. Crea la base de datos:
```bash
ssh root@64.23.242.78 "docker exec postgres psql -U admin -c 'CREATE DATABASE agencyflow;'"
```

4. Configura la conexion en tu app:
```
DATABASE_URL=postgresql://admin:TU_PASSWORD@postgres:5432/agencyflow
```

---

## Operaciones Comunes

### Actualizar un servicio

```bash
cd /opt/apps/infrastructure

# Rebuild y restart
docker compose build portfolio
docker compose up -d portfolio
```

### Ver logs en tiempo real

```bash
docker compose logs -f portfolio
docker compose logs -f traefik
```

### Reiniciar todos los servicios

```bash
docker compose restart
```

### Backup manual

```bash
./scripts/backup.sh
```

### Restaurar backup de PostgreSQL

```bash
gunzip < /opt/backups/FECHA/postgres_all.sql.gz | docker exec -i postgres psql -U admin
```

---

## Monitoreo con Uptime Kuma

1. Accede a https://status.esteban-ams.cl
2. Crea una cuenta de administrador
3. Agrega monitores:
   - **Portfolio**: HTTPS, https://portafolio.esteban-ams.cl
   - **Traefik**: TCP, localhost:443
   - **PostgreSQL**: TCP, postgres:5432 (solo interno)

### Configurar notificaciones

- Telegram
- Discord
- Email (via SMTP)
- Webhook

---

## Seguridad Adicional

### Cambiar puerto SSH (opcional)

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: Port 22 -> Port 2222

sudo ufw allow 2222
sudo ufw delete allow ssh
sudo systemctl restart sshd
```

### Deshabilitar login root

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: PermitRootLogin no
sudo systemctl restart sshd
```

### Revisar logs de seguridad

```bash
# Intentos de login fallidos
sudo fail2ban-client status sshd

# Logs del firewall
sudo ufw status verbose
```

---

## Troubleshooting

### Traefik no genera certificados

```bash
# Verificar logs de ACME
docker logs traefik 2>&1 | grep -i acme

# Verificar que el dominio resuelve correctamente
dig portafolio.esteban-ams.cl

# Verificar puertos abiertos
sudo ufw status
```

### Contenedor no inicia

```bash
# Ver logs detallados
docker logs nombre_contenedor

# Verificar configuracion
docker compose config

# Reiniciar contenedor
docker compose restart nombre_contenedor
```

### Error de conexion a PostgreSQL

```bash
# Verificar que PostgreSQL esta corriendo
docker ps | grep postgres

# Conectar manualmente
docker exec -it postgres psql -U admin

# Verificar red
docker network inspect internal
```

### Espacio en disco

```bash
# Ver uso de disco
df -h

# Limpiar imagenes Docker no usadas
docker system prune -a

# Limpiar logs de Docker
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

---

## Comparativa de Costos

| Configuracion | Apps | Costo Mensual |
|--------------|------|---------------|
| App Platform (1 app) | 1 | $5 |
| App Platform (3 apps) | 3 | $15 |
| **Droplet + Traefik** | **Ilimitadas** | **$12** |

Con esta infraestructura puedes agregar tantas aplicaciones como el Droplet soporte (con 2GB RAM, facilmente 5-10 apps pequeñas).

---

## Proximos Pasos Recomendados

1. **GitHub Actions**: Configurar CI/CD para deploy automatico
2. **Backups automaticos**: Agregar cron job para backup diario
3. **Alertas**: Configurar notificaciones en Uptime Kuma
4. **Logs centralizados**: Considerar Loki + Grafana si necesitas mas observabilidad
