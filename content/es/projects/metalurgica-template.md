---
title: Metalurgica Template
slug: metalurgica-template
technologies:
  - FastHTML
  - HTMX
  - CSS
  - Alpine.js
github: https://github.com/estebanmartinezsoto/metalurgica-spa
demo: null
featured: false
image: /static/images/metalurgica.jpg
excerpt: Template profesional B2B para empresas industriales construido con FastHTML. Diseno "Forja Moderna" con componentes reutilizables, galeria interactiva HTMX, y formularios de contacto/cotizacion.
---

# Metalurgica Template

Template web profesional disenado para empresas del sector industrial y metalurgico. Construido con FastHTML para demostrar que sitios corporativos modernos no necesitan frameworks JavaScript pesados.

## Concepto de Diseno

El diseno "Forja Moderna" combina:
- Estetica industrial (grises, naranjas, texturas metalicas)
- Tipografia bold y legible
- Imagenes de alto impacto
- UX clara para decision-makers B2B

```css
:root {
  /* Paleta Industrial */
  --steel-dark: #1a1a2e;
  --steel-medium: #2d2d44;
  --forge-orange: #e94560;
  --metal-gray: #4a4a5a;
  --spark-yellow: #f9a826;

  /* Tipografia Bold */
  --font-heading: 'Oswald', sans-serif;
  --font-body: 'Open Sans', sans-serif;
}
```

## Estructura del Sitio

```
/
├── Hero con video de fondo
├── Servicios (grid de cards)
├── Galeria de proyectos (HTMX)
├── Proceso de trabajo (timeline)
├── Testimonios
├── Formulario de cotizacion
└── Footer con mapa
```

## Componentes FastHTML

### Hero con Video

```python
def Hero():
    return Section(
        # Video de fondo
        Video(
            Source(src='/static/video/forge.mp4', type='video/mp4'),
            autoplay=True,
            muted=True,
            loop=True,
            cls='hero-video'
        ),

        # Overlay
        Div(cls='hero-overlay'),

        # Contenido
        Div(
            H1('Soluciones en Acero', cls='hero-title'),
            P('40 anos de experiencia en metalurgia industrial'),
            A('Solicitar Cotizacion', href='#cotizacion', cls='btn-primary'),
            cls='hero-content'
        ),

        cls='hero'
    )
```

### Galeria Interactiva con HTMX

```python
def GalleryGrid():
    """Grid de proyectos con carga dinamica."""
    return Div(
        # Filtros
        Div(
            Button('Todos', hx_get='/gallery?filter=all', hx_target='#gallery-items'),
            Button('Estructuras', hx_get='/gallery?filter=estructuras', hx_target='#gallery-items'),
            Button('Maquinaria', hx_get='/gallery?filter=maquinaria', hx_target='#gallery-items'),
            cls='gallery-filters'
        ),

        # Items (cargados via HTMX)
        Div(
            id='gallery-items',
            hx_get='/gallery?filter=all',
            hx_trigger='load'
        ),

        cls='gallery-section'
    )

@rt('/gallery')
def get(filter: str = 'all'):
    """Endpoint para cargar items de galeria."""
    projects = get_projects(filter)

    return Div(
        *[ProjectCard(p) for p in projects],
        cls='gallery-grid'
    )

def ProjectCard(project):
    return Div(
        Img(src=project.image, alt=project.title, loading='lazy'),
        Div(
            H3(project.title),
            P(project.description),
            cls='project-info'
        ),
        cls='project-card',
        **{'@click': f"$dispatch('open-modal', {{ id: {project.id} }})"}
    )
```

### Formulario de Cotizacion

```python
def QuoteForm():
    return Form(
        H2('Solicitar Cotizacion'),

        Div(
            Label('Nombre', fr='name'),
            Input(type='text', name='name', id='name', required=True),
            cls='form-group'
        ),

        Div(
            Label('Email', fr='email'),
            Input(type='email', name='email', id='email', required=True),
            cls='form-group'
        ),

        Div(
            Label('Telefono', fr='phone'),
            Input(type='tel', name='phone', id='phone'),
            cls='form-group'
        ),

        Div(
            Label('Tipo de Proyecto', fr='project_type'),
            Select(
                Option('Seleccionar...', value=''),
                Option('Estructuras metalicas'),
                Option('Maquinaria industrial'),
                Option('Reparaciones'),
                Option('Otro'),
                name='project_type',
                id='project_type'
            ),
            cls='form-group'
        ),

        Div(
            Label('Descripcion del proyecto', fr='description'),
            Textarea(name='description', id='description', rows=4),
            cls='form-group'
        ),

        Button('Enviar Solicitud', type='submit', cls='btn-primary'),

        hx_post='/quote',
        hx_target='#form-response',
        hx_swap='innerHTML',
        cls='quote-form'
    )

@rt('/quote')
async def post(name: str, email: str, phone: str, project_type: str, description: str):
    # Guardar cotizacion
    quote = save_quote(name, email, phone, project_type, description)

    # Enviar email de notificacion
    await send_notification_email(quote)

    return Div(
        H3('Solicitud Enviada'),
        P(f'Gracias {name}, nos pondremos en contacto pronto.'),
        cls='form-success'
    )
```

## Animaciones con Alpine.js

### Scroll Reveal

```html
<div x-data="{ shown: false }"
     x-intersect="shown = true"
     :class="shown ? 'animate-in' : 'animate-out'">
    <!-- Contenido -->
</div>
```

### Modal de Galeria

```html
<div x-data="{ open: false, project: null }"
     @open-modal.window="open = true; project = $event.detail">

    <div x-show="open"
         x-transition
         class="modal-overlay"
         @click.self="open = false">

        <div class="modal-content">
            <img :src="project?.image" :alt="project?.title">
            <h3 x-text="project?.title"></h3>
            <p x-text="project?.description"></p>
            <button @click="open = false">Cerrar</button>
        </div>
    </div>
</div>
```

## Optimizaciones

### Lazy Loading de Imagenes

```python
def OptimizedImage(src: str, alt: str):
    return Picture(
        Source(srcset=f'{src}?w=400', media='(max-width: 600px)'),
        Source(srcset=f'{src}?w=800', media='(max-width: 1200px)'),
        Img(src=f'{src}?w=1200', alt=alt, loading='lazy'),
        cls='responsive-image'
    )
```

### CSS Critico Inline

```python
def Page(*children):
    return Html(
        Head(
            # CSS critico inline para First Contentful Paint
            Style(CRITICAL_CSS),
            # CSS completo cargado async
            Link(rel='preload', href='/static/css/main.css', as_='style'),
            Link(rel='stylesheet', href='/static/css/main.css', media='print', onload="this.media='all'"),
        ),
        Body(*children)
    )
```

## Uso del Template

```bash
# Clonar repositorio
git clone https://github.com/estebanmartinezsoto/metalurgica-spa

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### Personalizacion

1. Editar `data/content.py` con informacion de la empresa
2. Reemplazar imagenes en `static/images/`
3. Ajustar colores en `static/css/variables.css`
4. Modificar formulario de cotizacion segun necesidades

## Por Que FastHTML

Este template demuestra que:
- No necesitas React para sitios corporativos
- HTMX permite interactividad sin bundle JavaScript
- Server-side rendering = mejor SEO
- Menos complejidad = mantenimiento mas facil
