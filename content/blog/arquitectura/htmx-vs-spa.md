---
title: HTMX vs SPA - Cuando usar cada uno
slug: htmx-vs-spa
date: 2024-10-05
tags:
  - HTMX
  - Arquitectura
  - Frontend
  - FastHTML
excerpt: Analisis practico de cuando elegir HTMX sobre un framework SPA como React o Vue.
---

# HTMX vs SPA: Una Decision Arquitectonica

Despues de construir aplicaciones con React, Vue, y recientemente con HTMX/FastHTML, tengo una perspectiva clara de cuando usar cada enfoque.

## El Problema con los SPAs

No me malinterpreten: React es excelente. Pero para muchas aplicaciones empresariales, un SPA introduce complejidad innecesaria:

```
SPA Tipico:
├── Frontend (React/Vue)
│   ├── State management (Redux/Vuex)
│   ├── Routing (React Router)
│   ├── API client (Axios/fetch)
│   ├── Build system (Webpack/Vite)
│   └── Testing (Jest/Cypress)
├── Backend (API)
│   ├── Serializers
│   ├── CORS config
│   └── Auth tokens
└── DevOps
    ├── 2 deployments
    └── 2 pipelines CI/CD
```

Para un ERP interno o un panel de admin, esto es **overkill**.

## La Filosofia HTMX

HTMX propone algo radical: el servidor envia HTML, no JSON.

```html
<!-- Un boton que actualiza solo una parte de la pagina -->
<button
    hx-post="/agregar-producto"
    hx-target="#carrito"
    hx-swap="innerHTML">
    Agregar al carrito
</button>

<div id="carrito">
    <!-- El servidor envia HTML aqui -->
</div>
```

El servidor responde con HTML listo para renderizar:

```python
@rt('/agregar-producto')
def post(producto_id: int):
    carrito = agregar_al_carrito(producto_id)
    # Retorna HTML, no JSON
    return Div(
        *[ItemCarrito(item) for item in carrito.items],
        P(f'Total: ${carrito.total}')
    )
```

## Comparativa Real

| Aspecto | SPA (React) | HTMX |
|---------|-------------|------|
| Tiempo inicial | 2-3 semanas | 2-3 dias |
| Lineas de codigo | 10,000+ | 2,000 |
| Dependencias | 50+ | 3-5 |
| Bundle size | 200KB+ | 14KB |
| SEO | Requiere SSR | Nativo |
| Caching | Complejo | HTTP estandar |

## Cuando Elegir HTMX

**Ideal para:**
- Paneles de administracion
- ERPs y sistemas internos
- Landing pages con interactividad
- Aplicaciones CRUD
- MVPs rapidos

**Ejemplos de mis proyectos:**
- ERP Market: POS completo con HTMX
- AgencyFlow: CRM multi-tenant
- Metalurgica: Sitio B2B con formularios

## Cuando Elegir SPA

**Necesario para:**
- Apps offline-first
- Editores complejos (Figma, Notion)
- Dashboards con graficos interactivos pesados
- Apps moviles hibridas

## Patron Hibrido

Lo mejor de ambos mundos: HTMX para el 90%, islas de JavaScript para lo complejo.

```html
<!-- HTMX para la estructura -->
<div hx-get="/dashboard" hx-trigger="load">
    Loading...
</div>

<!-- Alpine.js para interactividad local -->
<div x-data="{ open: false }">
    <button @click="open = !open">Menu</button>
    <nav x-show="open">...</nav>
</div>

<!-- Chart.js solo donde se necesita -->
<canvas id="grafico"
    x-data
    x-init="renderChart($el, await fetch('/api/datos').then(r => r.json()))">
</canvas>
```

## Mi Stack Actual

```
FastHTML + HTMX + Alpine.js
├── Server-side rendering (SEO, performance)
├── Partial updates (UX fluida)
├── Minimal JS (solo donde agrega valor)
└── Un solo deployment (simplicidad)
```

## Conclusion

HTMX no es "volver al pasado". Es reconocer que HTTP y HTML ya resuelven el 90% de los problemas de UI, y que agregar una capa de JavaScript solo tiene sentido cuando realmente lo necesitas.

Para mi proximo proyecto empresarial, HTMX sera mi primera opcion. React lo reservo para cuando realmente necesito un SPA.
