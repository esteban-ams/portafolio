# FastShip - Guia de Integracion

Esta guia explica como integrar FastShip con GitHub Actions para despliegues automaticos instantaneos.

## Que es FastShip?

FastShip es un servidor de webhooks que reemplaza a Watchtower. En lugar de esperar a que Watchtower detecte nuevas imagenes (cada 5 minutos), FastShip recibe una notificacion inmediata desde GitHub Actions y despliega al instante.

```
GitHub Actions (push image) --> webhook --> FastShip --> docker compose pull/up
```

## Configuracion en GitHub Actions

### 1. Agregar el secreto FASTSHIP_SECRET

En tu repositorio de GitHub:
1. Ve a **Settings** > **Secrets and variables** > **Actions**
2. Click en **New repository secret**
3. Nombre: `FASTSHIP_SECRET`
4. Valor: El mismo secreto configurado en el servidor (genera con `openssl rand -hex 32`)

### 2. Agregar el paso de deploy al workflow

Agrega este paso al final de tu workflow de CI/CD, despues de hacer push de la imagen:

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      # =======================================================================
      # DESPLIEGUE CON FASTSHIP
      # =======================================================================
      - name: Deploy to production
        run: |
          curl -X POST https://deploy.esteban-ams.cl/api/deploy/TU_SERVICIO \
            -H "X-FastShip-Secret: ${{ secrets.FASTSHIP_SECRET }}" \
            -H "Content-Type: application/json" \
            -d '{"image": "ghcr.io/${{ github.repository }}:${{ github.sha }}"}'
```

### 3. Servicios disponibles

Reemplaza `TU_SERVICIO` con uno de los siguientes nombres segun el proyecto:

| Proyecto | Endpoint | Imagen |
|----------|----------|--------|
| Portfolio | `/api/deploy/portfolio` | ghcr.io/esteban-ams/portafolio:latest |
| Komercia Cloud | `/api/deploy/komercia` | ghcr.io/esteban-ams/erp-market-django:latest |
| Komercia Landing | `/api/deploy/komercia-landing` | ghcr.io/esteban-ams/komercia-landing:latest |
| Metalurgica | `/api/deploy/metalurgica` | ghcr.io/esteban-ams/metalurgica-spa:latest |

## Ejemplo Completo: Komercia Cloud

```yaml
# .github/workflows/deploy.yml
name: Deploy Komercia Cloud

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=sha,prefix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

      - name: Deploy to production
        run: |
          response=$(curl -s -w "\n%{http_code}" -X POST \
            https://deploy.esteban-ams.cl/api/deploy/komercia \
            -H "X-FastShip-Secret: ${{ secrets.FASTSHIP_SECRET }}" \
            -H "Content-Type: application/json" \
            -d '{"image": "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}"}')

          http_code=$(echo "$response" | tail -n1)
          body=$(echo "$response" | sed '$d')

          echo "Response: $body"
          echo "HTTP Code: $http_code"

          if [ "$http_code" -ge 400 ]; then
            echo "::error::Deploy failed with HTTP $http_code"
            exit 1
          fi

      - name: Wait for deployment
        run: |
          echo "Waiting 30 seconds for deployment to complete..."
          sleep 30

          # Verificar health del servicio
          curl -f https://app.komercia.esteban-ams.cl/admin/login/ || exit 1
          echo "Deployment successful!"
```

## Verificacion y Rollback

### Ver historial de despliegues

```bash
curl https://deploy.esteban-ams.cl/api/deployments \
  -H "X-FastShip-Secret: ${{ secrets.FASTSHIP_SECRET }}"
```

### Rollback manual

```bash
curl -X POST https://deploy.esteban-ams.cl/api/rollback/komercia \
  -H "X-FastShip-Secret: ${{ secrets.FASTSHIP_SECRET }}"
```

### Dashboard Web

Accede al dashboard en: https://deploy.esteban-ams.cl

Credenciales configuradas en las variables de entorno del servidor.

## Migracion desde Watchtower

1. **Paso 1**: Agrega FastShip al docker-compose.yml (ya hecho)
2. **Paso 2**: Configura FASTSHIP_SECRET en el servidor y GitHub
3. **Paso 3**: Actualiza los workflows de CI/CD con el paso de deploy
4. **Paso 4**: Verifica que los deploys funcionan correctamente
5. **Paso 5**: Remueve los labels de Watchtower de los servicios
6. **Paso 6**: Remueve el servicio Watchtower del docker-compose.yml

## Troubleshooting

### El webhook falla con 401

- Verifica que FASTSHIP_SECRET sea el mismo en GitHub y en el servidor
- Asegurate de que la variable de entorno este cargada correctamente

### El deploy tarda mucho

- Revisa los logs de FastShip: `docker logs fastship`
- Verifica que el health check URL sea correcto
- Aumenta el timeout si el servicio tarda en iniciar

### Rollback automatico

FastShip ejecutara rollback automatico si:
- El health check falla despues del deploy
- Se alcanza el numero maximo de reintentos

Revisa los logs para ver que version se restauro.
