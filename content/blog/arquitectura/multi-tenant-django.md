---
title: Arquitectura Multi-Tenant en Django
slug: multi-tenant-django
date: 2024-06-15
tags:
  - Django
  - Arquitectura
  - SaaS
  - PostgreSQL
excerpt: Como disenar una arquitectura multi-tenant robusta en Django para aplicaciones SaaS empresariales.
---

# Arquitectura Multi-Tenant en Django

Cuando construyes un SaaS empresarial, una de las decisiones mas importantes es como aislar los datos de cada cliente. En este articulo comparto el patron que use en ERP Market para manejar multiples empresas con total aislamiento de datos.

## El Problema

Imagina un ERP donde multiples minimarkets usan el mismo sistema. Cada uno tiene sus productos, ventas, facturas y usuarios. **Nunca** deben ver los datos de otro.

## Estrategias de Multi-Tenancy

Hay tres enfoques principales:

| Estrategia | Aislamiento | Complejidad | Costo |
|------------|-------------|-------------|-------|
| Base de datos por tenant | Alto | Alta | Alto |
| Schema por tenant | Medio | Media | Medio |
| Rows compartidos | Bajo | Baja | Bajo |

Para ERP Market elegí **rows compartidos con filtrado automatico** por su balance entre simplicidad y costo.

## Implementacion

### 1. Modelo Base con Company

```python
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200)
    rut = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=True)

class CompanyBoundModel(models.Model):
    """Modelo base que pertenece a una empresa."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True
```

### 2. Manager con Filtrado Automatico

```python
class CompanyManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)

    def get_queryset(self):
        # El filtrado real se hace en las vistas
        return super().get_queryset()
```

### 3. Middleware para Contexto

```python
from threading import local

_thread_locals = local()

def get_current_company():
    return getattr(_thread_locals, 'company', None)

class CompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            _thread_locals.company = request.user.profile.company
        response = self.get_response(request)
        return response
```

### 4. Mixin para Vistas

```python
class CompanyFilterMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        company = get_current_company()
        if company and hasattr(qs.model, 'company'):
            return qs.filter(company=company)
        return qs
```

## Validaciones Criticas

Nunca confies solo en el filtrado. Agrega validaciones explicitas:

```python
def crear_venta(request, producto_id):
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        company=request.user.profile.company  # Validacion explicita
    )
    # ...
```

## Resultados

Con este patron, ERP Market maneja multiples empresas con:

- **0 filtraciones de datos** entre tenants
- **Queries simples** sin JOINs complejos
- **Migraciones unicas** para todos los tenants
- **Backup centralizado** de toda la plataforma

## Conclusion

El multi-tenancy por rows es ideal para SaaS donde el costo de infraestructura importa. La clave es ser **paranoico** con las validaciones y nunca asumir que el filtrado automatico es suficiente.
