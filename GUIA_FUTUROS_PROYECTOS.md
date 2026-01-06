# Guía para Futuros Proyectos

Esta guía cubre dos escenarios principales de despliegue.

---

## Escenario A: Aplicación Standalone (Tu Infraestructura)

**Usar para:** Proyectos propios, SaaS, aplicaciones que requieren base de datos, proyectos complejos.

**Ejemplo:** AgencyFlow, Komercia, aplicaciones multi-tenant.

**Costo:** $0 adicional (ya tienes el Droplet).

### Agregar a tu infraestructura existente

```bash
# 1. Crear Dockerfile en el proyecto
# 2. Agregar a docker-compose.yml
# 3. Agregar a sync-and-deploy.sh
# 4. Ejecutar: ./infrastructure/scripts/sync-and-deploy.sh
```

Ver sección "Agregar Nuevos Proyectos" en [DEPLOYMENT.md](./DEPLOYMENT.md).

---

## Escenario B: Landing Page para Cliente (App Platform)

**Usar para:** Landing pages, sitios estáticos, proyectos de clientes, sitios simples.

**Ejemplo:** Landing page para empresa X, sitio corporativo, portafolio de cliente.

**Costo:** ~$5 USD/mes por app (lo paga el cliente).

### Paso 1: Preparar el Proyecto

#### Estructura mínima para FastHTML

```
mi-landing/
├── main.py              # Aplicación FastHTML
├── requirements.txt     # Dependencias
├── runtime.txt          # python-3.11
├── Procfile             # web: gunicorn main:app ...
├── static/              # CSS, JS, imágenes
│   ├── css/
│   ├── js/
│   └── images/
└── .gitignore
```

#### requirements.txt

```
python-fasthtml>=0.6.0
gunicorn>=21.0
uvicorn>=0.30.0
python-dotenv>=1.0
```

#### runtime.txt

```
python-3.11
```

#### Procfile

```
web: gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

#### main.py (ejemplo mínimo)

```python
from fasthtml.common import *

app, rt = fast_app(
    pico=False,
    static_path='static',
    hdrs=(
        Link(rel='stylesheet', href='/static/css/styles.css'),
    )
)

@rt('/')
def get():
    return Html(
        Head(Title("Mi Landing Page")),
        Body(
            H1("Bienvenido"),
            P("Landing page para cliente"),
        )
    )

# Para producción (App Platform)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    serve(port=port)
```

### Paso 2: Subir a GitHub

```bash
# Crear repo en cuenta del cliente o en la tuya
git init
git add .
git commit -m "Initial commit"
git remote add origin git@github.com:USUARIO/mi-landing.git
git push -u origin main
```

### Paso 3: Crear App en DigitalOcean (cuenta del cliente)

1. El cliente crea cuenta en [DigitalOcean](https://cloud.digitalocean.com)
2. Conecta su GitHub (o le das acceso al repo)
3. Crear App:
   - **Create App** → **GitHub** → Seleccionar repo
   - **Type**: Web Service
   - **Plan**: Basic ($5/mes)
   - **Region**: NYC o más cercano al cliente
   - **Branch**: main

### Paso 4: Configurar Dominio del Cliente

#### Opción A: Subdominio de DigitalOcean (gratis, rápido)
- La app tendrá URL tipo: `mi-landing-xxxxx.ondigitalocean.app`
- Usar para demos o mientras se configura dominio propio

#### Opción B: Dominio propio del cliente

1. En App Platform → Settings → Domains → Add Domain
2. Agregar: `www.clientedominio.cl`
3. Configurar DNS del cliente:

```
Tipo    Host    Valor
CNAME   www     mi-landing-xxxxx.ondigitalocean.app.
A       @       <IP que da DigitalOcean>
```

### Paso 5: Variables de Entorno (si necesita)

En App Platform → Settings → App-Level Environment Variables:

```
CONTACT_EMAIL=cliente@empresa.cl
RESEND_API_KEY=re_xxxxx  # Si tiene formulario de contacto
```

### Paso 6: Deploy Automático

App Platform hace deploy automático en cada push a `main`.

```bash
# Para actualizar la landing:
git add .
git commit -m "Update: cambios en landing"
git push origin main
# App Platform detecta y redespliega automáticamente (~2-3 min)
```

---

## Comparativa: ¿Cuál Usar?

| Criterio | Tu Droplet | App Platform Cliente |
|----------|------------|---------------------|
| **Costo** | $0 (ya pagado) | $5/mes al cliente |
| **Dominio** | *.esteban-ams.cl | Dominio del cliente |
| **Base de datos** | ✅ PostgreSQL incluido | ❌ Costo extra |
| **Complejidad** | Apps complejas | Landing/sitios simples |
| **Mantenimiento** | Tú | DigitalOcean |
| **SSL** | ✅ Let's Encrypt | ✅ Automático |
| **Escalabilidad** | Manual | Automática |

---

## Plantillas Rápidas

### Landing Page FastHTML (Copiar y usar)

```bash
# Clonar plantilla base
git clone git@github.com:esteban-ams/portafolio.git mi-nueva-landing
cd mi-nueva-landing

# Limpiar para usar como base
rm -rf .git content/ infrastructure/ DEPLOYMENT.md GUIA_FUTUROS_PROYECTOS.md
rm -rf components/blog.py pages/blog.py  # Si no necesitas blog

# Iniciar nuevo repo
git init
git add .
git commit -m "Initial: Landing page base"
```

### Estructura Recomendada para Landings

```
landing-cliente/
├── main.py                 # Rutas principales
├── components/
│   ├── layout.py          # Header, Footer, Page wrapper
│   ├── hero.py            # Sección hero
│   ├── features.py        # Features/servicios
│   ├── testimonials.py    # Testimonios
│   ├── pricing.py         # Precios (si aplica)
│   ├── contact.py         # Formulario contacto
│   └── cta.py             # Call to action
├── data/
│   └── content.py         # Todo el contenido (fácil de editar)
├── static/
│   ├── css/
│   │   └── styles.css     # Estilos personalizados
│   ├── js/
│   └── images/
│       └── logo.png
├── services/
│   └── email.py           # Envío de emails (Resend)
├── requirements.txt
├── runtime.txt
├── Procfile
└── .gitignore
```

---

## Checklist: Nueva Landing para Cliente

- [ ] Crear repo (GitHub del cliente o tuyo)
- [ ] Copiar estructura base de FastHTML
- [ ] Personalizar `data/content.py` con contenido del cliente
- [ ] Personalizar estilos en `static/css/`
- [ ] Agregar logo e imágenes del cliente
- [ ] Probar localmente: `python main.py`
- [ ] Push a GitHub
- [ ] Cliente crea cuenta DigitalOcean
- [ ] Crear App Platform conectando al repo
- [ ] Configurar dominio del cliente
- [ ] Configurar variables de entorno (email, API keys)
- [ ] Probar formulario de contacto
- [ ] Entregar al cliente

---

## Checklist: Nueva App en Tu Infraestructura

- [ ] Crear Dockerfile en el proyecto
- [ ] Agregar servicio en `infrastructure/docker-compose.yml`
- [ ] Agregar ruta en `infrastructure/scripts/sync-and-deploy.sh`
- [ ] Crear base de datos si necesita: `docker exec postgres psql -U admin -c 'CREATE DATABASE miapp;'`
- [ ] Ejecutar `./infrastructure/scripts/sync-and-deploy.sh`
- [ ] Verificar: `curl -I https://miapp.esteban-ams.cl`
- [ ] Commit cambios en infraestructura

---

## Comandos Útiles

### Tu Infraestructura

```bash
# Desplegar todo
./infrastructure/scripts/sync-and-deploy.sh

# Ver estado
ssh root@64.23.242.78 "cd /opt/infrastructure && docker compose ps"

# Logs de un servicio
ssh root@64.23.242.78 "docker logs portfolio --tail 100 -f"

# Reiniciar servicio
ssh root@64.23.242.78 "cd /opt/infrastructure && docker compose restart portfolio"

# Entrar a contenedor
ssh root@64.23.242.78 "docker exec -it komercia bash"

# Ver uso de recursos
ssh root@64.23.242.78 "docker stats --no-stream"
```

### App Platform (desde doctl)

```bash
# Listar apps
doctl apps list

# Ver logs de app
doctl apps logs APP_ID

# Forzar redeploy
doctl apps create-deployment APP_ID

# Borrar app
doctl apps delete APP_ID
```

---

## Contactos y Recursos

- **Droplet IP**: 64.23.242.78
- **Dominio principal**: esteban-ams.cl
- **DigitalOcean Dashboard**: https://cloud.digitalocean.com
- **GitHub**: https://github.com/esteban-ams

### URLs Activas

| Servicio | URL |
|----------|-----|
| Portfolio | https://esteban-ams.cl |
| Komercia | https://komercia.esteban-ams.cl |
| Metalurgica | https://metalurgica.esteban-ams.cl |
| Status | https://status.esteban-ams.cl |
