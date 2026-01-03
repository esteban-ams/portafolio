---
title: Introduccion a FastHTML
slug: fasthtml-introduccion
date: 2024-01-15
tags:
  - Python
  - FastHTML
  - Web Development
excerpt: Descubre como construir aplicaciones web modernas con Python y FastHTML.
---

# Introduccion a FastHTML

FastHTML es un framework moderno para construir aplicaciones web con Python. Combina la simplicidad de Python con el poder de HTMX para crear interfaces dinamicas sin escribir JavaScript.

## Por que FastHTML

- **Simplicidad**: Escribe componentes como funciones Python
- **Rendimiento**: Renderizado del lado del servidor, sin JavaScript pesado
- **Productividad**: Desarrollo rapido con hot reload

## Ejemplo basico

```python
from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Div(
        H1('Hello World!'),
        P('Bienvenido a FastHTML')
    )

serve()
```

## Componentes reutilizables

En FastHTML, los componentes son simplemente funciones:

```python
def Card(title, content):
    return Div(
        H3(title),
        P(content),
        cls='card'
    )

# Uso
Card('Mi Titulo', 'Contenido de la card')
```

## Integracion con HTMX

FastHTML se integra nativamente con HTMX para actualizaciones parciales:

```python
@rt('/contador')
def get():
    return Div(
        Span('0', id='count'),
        Button(
            'Incrementar',
            hx_post='/incrementar',
            hx_target='#count'
        )
    )
```

## Conclusion

FastHTML es una excelente opcion para desarrolladores Python que quieren crear aplicaciones web modernas sin la complejidad de frameworks JavaScript.
