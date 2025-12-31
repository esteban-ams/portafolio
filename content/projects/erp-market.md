---
title: ERP Market
slug: erp-market
technologies:
  - Django
  - PostgreSQL
  - HTMX
  - WeasyPrint
  - Docker
  - Celery
github: https://github.com/estebanmartinezsoto/erp-market-django
demo: null
featured: true
image: /static/images/erp-market.jpg
excerpt: Sistema ERP completo para retail con arquitectura multi-tenant, facturacion electronica SII Chile, POS tactil, gestion de inventario con costeo promedio ponderado, e integracion con impresoras termicas y balanzas digitales.
---

# ERP Market

Sistema de gestion empresarial completo disenado especificamente para minimarkets y tiendas de retail en Chile. Construido con arquitectura multi-tenant que permite a multiples empresas usar la misma instancia con total aislamiento de datos.

## El Problema

Los minimarkets en Chile enfrentan desafios unicos:
- Obligacion legal de emitir boletas electronicas (SII)
- Necesidad de controlar inventario con multiples metodos de costeo
- Integracion con hardware especializado (balanzas, impresoras termicas)
- Operacion continua sin tolerancia a caidas

Las soluciones existentes eran demasiado caras o no se adaptaban a la realidad chilena.

## Solucion

ERP Market es un sistema integral que cubre todo el ciclo de operacion:

### Punto de Venta (POS)

```
┌─────────────────────────────────────────────┐
│  POS Tactil                                 │
├─────────────────────────────────────────────┤
│  [Producto 1]  [Producto 2]  [Producto 3]   │
│  [Producto 4]  [Producto 5]  [Producto 6]   │
├─────────────────────────────────────────────┤
│  Carrito:                                   │
│  - Pan x2 ............ $1.200              │
│  - Leche x1 .......... $1.500              │
│  ─────────────────────────────              │
│  Total: $2.700                              │
├─────────────────────────────────────────────┤
│  [Efectivo] [Tarjeta] [Mixto]              │
└─────────────────────────────────────────────┘
```

- Interfaz tactil optimizada para pantallas de 10"
- Busqueda por codigo de barras, nombre o codigo interno
- Integracion con balanzas digitales para productos pesables
- Impresion termica de boletas en tiempo real

### Facturacion Electronica SII

Integracion completa con el Servicio de Impuestos Internos de Chile:

- Generacion automatica de DTE (Documentos Tributarios Electronicos)
- Firma digital con certificado .pfx
- Envio automatico al SII con reintentos
- Generacion de PDF con timbre electronico (TED)
- Soporte para: Boletas (39), Facturas (33), Notas de Credito (61)

### Gestion de Inventario

| Caracteristica | Descripcion |
|----------------|-------------|
| Costeo PPP | Promedio Ponderado Permanente automatico |
| Alertas de stock | Notificaciones cuando productos bajan del minimo |
| Trazabilidad | Historial completo de movimientos por producto |
| Multi-bodega | Soporte para multiples ubicaciones |

### Arquitectura Multi-Tenant

```python
class CompanyBoundModel(models.Model):
    """Todos los modelos heredan de aqui para aislamiento."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        abstract = True

# Middleware automatico filtra por empresa del usuario
class CompanyMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            _thread_locals.company = request.user.profile.company
        return self.get_response(request)
```

## Stack Tecnico

- **Backend**: Django 4.2 con Django REST Framework
- **Frontend**: HTMX + Alpine.js (sin SPA)
- **Base de datos**: PostgreSQL con indices optimizados
- **Tareas asincronas**: Celery + Redis
- **PDF**: WeasyPrint para documentos tributarios
- **Contenedores**: Docker Compose para desarrollo y produccion

## Resultados

- **0 filtraciones** de datos entre tenants en 2 anos de operacion
- **< 200ms** tiempo de respuesta promedio en POS
- **99.9%** uptime en produccion
- **100%** de boletas aceptadas por SII

## Aprendizajes

Este proyecto me enseno la importancia de:

1. **Validacion paranoica** en sistemas multi-tenant
2. **Manejo robusto de errores** en integraciones externas
3. **Diseno para offline-first** en operaciones criticas
4. **Testing exhaustivo** de flujos de facturacion
