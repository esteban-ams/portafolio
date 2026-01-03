---
title: HTMX vs SPA - When to use each
slug: htmx-vs-spa
date: 2024-10-05
tags:
  - HTMX
  - Architecture
  - Frontend
  - FastHTML
excerpt: Practical analysis of when to choose HTMX over a SPA framework like React or Vue.
---

# HTMX vs SPA: An Architectural Decision

After building applications with React, Vue, and recently with HTMX/FastHTML, I have a clear perspective on when to use each approach.

## The Problem with SPAs

Don't get me wrong: React is excellent. But for many enterprise applications, a SPA introduces unnecessary complexity:

```
Typical SPA:
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
    └── 2 CI/CD pipelines
```

For an internal ERP or admin panel, this is **overkill**.

## The HTMX Philosophy

HTMX proposes something radical: the server sends HTML, not JSON.

```html
<!-- A button that updates only part of the page -->
<button
    hx-post="/add-product"
    hx-target="#cart"
    hx-swap="innerHTML">
    Add to cart
</button>

<div id="cart">
    <!-- Server sends HTML here -->
</div>
```

The server responds with ready-to-render HTML:

```python
@rt('/add-product')
def post(product_id: int):
    cart = add_to_cart(product_id)
    # Returns HTML, not JSON
    return Div(
        *[CartItem(item) for item in cart.items],
        P(f'Total: ${cart.total}')
    )
```

## Real Comparison

| Aspect | SPA (React) | HTMX |
|--------|-------------|------|
| Initial time | 2-3 weeks | 2-3 days |
| Lines of code | 10,000+ | 2,000 |
| Dependencies | 50+ | 3-5 |
| Bundle size | 200KB+ | 14KB |
| SEO | Requires SSR | Native |
| Caching | Complex | Standard HTTP |

## When to Choose HTMX

**Ideal for:**
- Admin panels
- ERPs and internal systems
- Landing pages with interactivity
- CRUD applications
- Rapid MVPs

**Examples from my projects:**
- ERP Market: Complete POS with HTMX
- AgencyFlow: Multi-tenant CRM
- Metalurgica: B2B site with forms

## When to Choose SPA

**Necessary for:**
- Offline-first apps
- Complex editors (Figma, Notion)
- Dashboards with heavy interactive charts
- Hybrid mobile apps

## Hybrid Pattern

Best of both worlds: HTMX for 90%, JavaScript islands for the complex parts.

```html
<!-- HTMX for structure -->
<div hx-get="/dashboard" hx-trigger="load">
    Loading...
</div>

<!-- Alpine.js for local interactivity -->
<div x-data="{ open: false }">
    <button @click="open = !open">Menu</button>
    <nav x-show="open">...</nav>
</div>

<!-- Chart.js only where needed -->
<canvas id="chart"
    x-data
    x-init="renderChart($el, await fetch('/api/data').then(r => r.json()))">
</canvas>
```

## My Current Stack

```
FastHTML + HTMX + Alpine.js
├── Server-side rendering (SEO, performance)
├── Partial updates (fluid UX)
├── Minimal JS (only where it adds value)
└── Single deployment (simplicity)
```

## Conclusion

HTMX is not "going back to the past". It's recognizing that HTTP and HTML already solve 90% of UI problems, and that adding a JavaScript layer only makes sense when you really need it.

For my next enterprise project, HTMX will be my first choice. I'll reserve React for when I truly need a SPA.
