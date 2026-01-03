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
excerpt: Complete ERP system for retail with multi-tenant architecture, Chilean SII electronic invoicing, touch POS, inventory management with weighted average costing, and integration with thermal printers and digital scales.
---

# ERP Market

Complete enterprise management system specifically designed for minimarkets and retail stores in Chile. Built with multi-tenant architecture that allows multiple companies to use the same instance with complete data isolation.

## The Problem

Minimarkets in Chile face unique challenges:
- Legal obligation to issue electronic receipts (SII)
- Need to control inventory with multiple costing methods
- Integration with specialized hardware (scales, thermal printers)
- Continuous operation with zero downtime tolerance

Existing solutions were too expensive or didn't adapt to Chilean reality.

## Solution

ERP Market is a comprehensive system covering the entire operation cycle:

### Point of Sale (POS)

```
┌─────────────────────────────────────────────┐
│  Touch POS                                  │
├─────────────────────────────────────────────┤
│  [Product 1]  [Product 2]  [Product 3]      │
│  [Product 4]  [Product 5]  [Product 6]      │
├─────────────────────────────────────────────┤
│  Cart:                                      │
│  - Bread x2 ............ $1,200            │
│  - Milk x1 ............. $1,500            │
│  ─────────────────────────────              │
│  Total: $2,700                              │
├─────────────────────────────────────────────┤
│  [Cash] [Card] [Mixed]                      │
└─────────────────────────────────────────────┘
```

- Touch interface optimized for 10" screens
- Search by barcode, name, or internal code
- Integration with digital scales for weighable products
- Real-time thermal receipt printing

### SII Electronic Invoicing

Complete integration with Chile's Internal Revenue Service:

- Automatic DTE (Electronic Tax Documents) generation
- Digital signature with .pfx certificate
- Automatic submission to SII with retries
- PDF generation with electronic stamp (TED)
- Support for: Receipts (39), Invoices (33), Credit Notes (61)

### Inventory Management

| Feature | Description |
|---------|-------------|
| PPP Costing | Automatic Perpetual Weighted Average |
| Stock alerts | Notifications when products fall below minimum |
| Traceability | Complete movement history per product |
| Multi-warehouse | Support for multiple locations |

### Multi-Tenant Architecture

```python
class CompanyBoundModel(models.Model):
    """All models inherit from here for isolation."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        abstract = True

# Automatic middleware filters by user's company
class CompanyMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            _thread_locals.company = request.user.profile.company
        return self.get_response(request)
```

## Tech Stack

- **Backend**: Django 4.2 with Django REST Framework
- **Frontend**: HTMX + Alpine.js (no SPA)
- **Database**: PostgreSQL with optimized indexes
- **Async tasks**: Celery + Redis
- **PDF**: WeasyPrint for tax documents
- **Containers**: Docker Compose for development and production

## Results

- **0 data leaks** between tenants in 2 years of operation
- **< 200ms** average response time in POS
- **99.9%** production uptime
- **100%** of receipts accepted by SII

## Learnings

This project taught me the importance of:

1. **Paranoid validation** in multi-tenant systems
2. **Robust error handling** in external integrations
3. **Offline-first design** for critical operations
4. **Exhaustive testing** of invoicing flows
