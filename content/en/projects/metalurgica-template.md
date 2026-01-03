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
excerpt: Professional B2B template for industrial companies built with FastHTML. "Modern Forge" design with reusable components, interactive HTMX gallery, and contact/quote forms.
---

# Metalurgica Template

Professional web template designed for industrial and metallurgical sector companies. Built with FastHTML to demonstrate that modern corporate sites don't need heavy JavaScript frameworks.

## Design Concept

The "Modern Forge" design combines:
- Industrial aesthetics (grays, oranges, metallic textures)
- Bold and readable typography
- High-impact images
- Clear UX for B2B decision-makers

```css
:root {
  /* Industrial Palette */
  --steel-dark: #1a1a2e;
  --steel-medium: #2d2d44;
  --forge-orange: #e94560;
  --metal-gray: #4a4a5a;
  --spark-yellow: #f9a826;

  /* Bold Typography */
  --font-heading: 'Oswald', sans-serif;
  --font-body: 'Open Sans', sans-serif;
}
```

## Site Structure

```
/
├── Hero with background video
├── Services (card grid)
├── Project gallery (HTMX)
├── Work process (timeline)
├── Testimonials
├── Quote request form
└── Footer with map
```

## FastHTML Components

### Hero with Video

```python
def Hero():
    return Section(
        # Background video
        Video(
            Source(src='/static/video/forge.mp4', type='video/mp4'),
            autoplay=True,
            muted=True,
            loop=True,
            cls='hero-video'
        ),

        # Overlay
        Div(cls='hero-overlay'),

        # Content
        Div(
            H1('Steel Solutions', cls='hero-title'),
            P('40 years of experience in industrial metallurgy'),
            A('Request Quote', href='#quote', cls='btn-primary'),
            cls='hero-content'
        ),

        cls='hero'
    )
```

### Interactive Gallery with HTMX

```python
def GalleryGrid():
    """Project grid with dynamic loading."""
    return Div(
        # Filters
        Div(
            Button('All', hx_get='/gallery?filter=all', hx_target='#gallery-items'),
            Button('Structures', hx_get='/gallery?filter=structures', hx_target='#gallery-items'),
            Button('Machinery', hx_get='/gallery?filter=machinery', hx_target='#gallery-items'),
            cls='gallery-filters'
        ),

        # Items (loaded via HTMX)
        Div(
            id='gallery-items',
            hx_get='/gallery?filter=all',
            hx_trigger='load'
        ),

        cls='gallery-section'
    )

@rt('/gallery')
def get(filter: str = 'all'):
    """Endpoint to load gallery items."""
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

### Quote Request Form

```python
def QuoteForm():
    return Form(
        H2('Request Quote'),

        Div(
            Label('Name', fr='name'),
            Input(type='text', name='name', id='name', required=True),
            cls='form-group'
        ),

        Div(
            Label('Email', fr='email'),
            Input(type='email', name='email', id='email', required=True),
            cls='form-group'
        ),

        Div(
            Label('Phone', fr='phone'),
            Input(type='tel', name='phone', id='phone'),
            cls='form-group'
        ),

        Div(
            Label('Project Type', fr='project_type'),
            Select(
                Option('Select...', value=''),
                Option('Metal structures'),
                Option('Industrial machinery'),
                Option('Repairs'),
                Option('Other'),
                name='project_type',
                id='project_type'
            ),
            cls='form-group'
        ),

        Div(
            Label('Project description', fr='description'),
            Textarea(name='description', id='description', rows=4),
            cls='form-group'
        ),

        Button('Send Request', type='submit', cls='btn-primary'),

        hx_post='/quote',
        hx_target='#form-response',
        hx_swap='innerHTML',
        cls='quote-form'
    )

@rt('/quote')
async def post(name: str, email: str, phone: str, project_type: str, description: str):
    # Save quote
    quote = save_quote(name, email, phone, project_type, description)

    # Send notification email
    await send_notification_email(quote)

    return Div(
        H3('Request Sent'),
        P(f'Thanks {name}, we will contact you soon.'),
        cls='form-success'
    )
```

## Animations with Alpine.js

### Scroll Reveal

```html
<div x-data="{ shown: false }"
     x-intersect="shown = true"
     :class="shown ? 'animate-in' : 'animate-out'">
    <!-- Content -->
</div>
```

### Gallery Modal

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
            <button @click="open = false">Close</button>
        </div>
    </div>
</div>
```

## Optimizations

### Image Lazy Loading

```python
def OptimizedImage(src: str, alt: str):
    return Picture(
        Source(srcset=f'{src}?w=400', media='(max-width: 600px)'),
        Source(srcset=f'{src}?w=800', media='(max-width: 1200px)'),
        Img(src=f'{src}?w=1200', alt=alt, loading='lazy'),
        cls='responsive-image'
    )
```

### Critical CSS Inline

```python
def Page(*children):
    return Html(
        Head(
            # Critical CSS inline for First Contentful Paint
            Style(CRITICAL_CSS),
            # Full CSS loaded async
            Link(rel='preload', href='/static/css/main.css', as_='style'),
            Link(rel='stylesheet', href='/static/css/main.css', media='print', onload="this.media='all'"),
        ),
        Body(*children)
    )
```

## Template Usage

```bash
# Clone repository
git clone https://github.com/estebanmartinezsoto/metalurgica-spa

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Customization

1. Edit `data/content.py` with company information
2. Replace images in `static/images/`
3. Adjust colors in `static/css/variables.css`
4. Modify quote form as needed

## Why FastHTML

This template demonstrates that:
- You don't need React for corporate sites
- HTMX enables interactivity without JavaScript bundles
- Server-side rendering = better SEO
- Less complexity = easier maintenance
