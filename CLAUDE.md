# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website built with FastHTML (Python), HTMX, and Alpine.js. Features a light theme with bold personality, smooth animations, and a full-featured blog.

## Tech Stack

- **FastHTML**: Python web framework for hypermedia-driven apps (NOT FastAPI compatible)
- **HTMX**: Server-side rendering with partial page updates via HTML attributes
- **Alpine.js**: Lightweight JS for animations and UI interactions
- **CSS**: Custom design system with CSS variables, no frameworks

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (http://localhost:5001)
python main.py

# Run with live reload (if configured)
python main.py --reload
```

## Architecture

```
portafolio/
├── main.py              # App entry, routes, FastHTML config
├── components/          # Reusable FT components (layout, hero, etc.)
├── pages/               # Full page handlers (blog list, blog post)
├── data/content.py      # All site content - EDIT THIS to customize
├── static/
│   ├── css/main.css     # All styles, CSS variables, responsive design
│   ├── js/              # Custom JS if needed
│   └── images/          # Project images, about photo
└── requirements.txt
```

## FastHTML Patterns

### FT Components (FastTags)
```python
from fasthtml.common import *

# Components are functions returning FT objects
def Card(title, content):
    return Div(H3(title), P(content), cls='card')

# Attributes: cls→class, fr→for, True→attr only, False→omit
# Special chars in attrs: **{'@click': "handler()"}
```

### Routing
```python
app, rt = fast_app(pico=False, hdrs=(...), static_path='static')

@rt('/')
def get(): return Page(...)

@rt('/blog/{slug}')
def get(slug: str): return blog_post(slug)

@rt('/contact')
async def post(name: str, email: str, message: str):
    return Div('Success', id='response')  # HTMX partial
```

### HTMX Integration
```python
# Add hx_* attributes for interactivity
Form(
    Input(name='email'),
    Button('Submit'),
    hx_post='/contact',        # POST to this endpoint
    hx_target='#response',     # Replace this element
    hx_swap='innerHTML'        # Swap strategy
)
```

### Alpine.js Integration
```python
# Use **{} for special attributes
Div(
    cls='card',
    **{'x-data': '{ open: false }',
       '@click': 'open = !open',
       'x-show': 'open'}
)
```

## Customization

Edit `data/content.py` to change:
- Site metadata (`site_config`)
- Hero section text (`hero_content`)
- Work experience (`experience_data`)
- Skills categories (`skills_data`)
- Projects (`projects_data`)
- About section (`about_content`)
- Blog posts (`blog_posts`)

## CSS Design System

CSS variables are in `static/css/main.css`:
- Colors: `--color-primary`, `--color-secondary`, `--color-accent`
- Typography: `--font-sans`, `--font-mono`
- Spacing: `--space-sm` through `--space-4xl`
- Shadows, radii, transitions defined

## Key Files to Know

- `components/hero.py`: Contains `SvgIcon()` helper for inline SVGs
- `components/layout.py`: `Page()` wrapper, `Navbar()`, section helpers
- `pages/blog.py`: Blog list/post pages with basic markdown rendering
- `static/css/main.css`: Complete stylesheet with responsive breakpoints

## Notes

- FastHTML uses `serve()` instead of `if __name__ == "__main__"`
- Use `NotStr()` or `Safe()` for unescaped HTML (SVG icons)
- Use `ft_hx('section', ...)` for HTML5 semantic elements not in common imports
- HTMX requests return partials; full requests return complete pages
- Alpine.js x-intersect used for scroll-triggered animations
