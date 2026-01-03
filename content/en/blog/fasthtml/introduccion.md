---
title: Introduction to FastHTML
slug: fasthtml-introduccion
date: 2024-01-15
tags:
  - Python
  - FastHTML
  - Web Development
excerpt: Discover how to build modern web applications with Python and FastHTML.
---

# Introduction to FastHTML

FastHTML is a modern framework for building web applications with Python. It combines Python's simplicity with the power of HTMX to create dynamic interfaces without writing JavaScript.

## Why FastHTML

- **Simplicity**: Write components as Python functions
- **Performance**: Server-side rendering, no heavy JavaScript
- **Productivity**: Fast development with hot reload

## Basic Example

```python
from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Div(
        H1('Hello World!'),
        P('Welcome to FastHTML')
    )

serve()
```

## Reusable Components

In FastHTML, components are simply functions:

```python
def Card(title, content):
    return Div(
        H3(title),
        P(content),
        cls='card'
    )

# Usage
Card('My Title', 'Card content')
```

## HTMX Integration

FastHTML integrates natively with HTMX for partial updates:

```python
@rt('/counter')
def get():
    return Div(
        Span('0', id='count'),
        Button(
            'Increment',
            hx_post='/increment',
            hx_target='#count'
        )
    )
```

## Conclusion

FastHTML is an excellent choice for Python developers who want to create modern web applications without the complexity of JavaScript frameworks.
