---
title: Multi-Tenant Architecture in Django
slug: multi-tenant-django
date: 2024-06-15
tags:
  - Django
  - Architecture
  - SaaS
  - PostgreSQL
excerpt: How to design a robust multi-tenant architecture in Django for enterprise SaaS applications.
---

# Multi-Tenant Architecture in Django

When building an enterprise SaaS, one of the most important decisions is how to isolate each customer's data. In this article I share the pattern I used in ERP Market to handle multiple companies with complete data isolation.

## The Problem

Imagine an ERP where multiple minimarkets use the same system. Each one has its own products, sales, invoices, and users. They should **never** see each other's data.

## Multi-Tenancy Strategies

There are three main approaches:

| Strategy | Isolation | Complexity | Cost |
|----------|-----------|------------|------|
| Database per tenant | High | High | High |
| Schema per tenant | Medium | Medium | Medium |
| Shared rows | Low | Low | Low |

For ERP Market I chose **shared rows with automatic filtering** for its balance between simplicity and cost.

## Implementation

### 1. Base Model with Company

```python
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200)
    rut = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=True)

class CompanyBoundModel(models.Model):
    """Base model that belongs to a company."""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        abstract = True
```

### 2. Manager with Automatic Filtering

```python
class CompanyManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)

    def get_queryset(self):
        # Actual filtering is done in views
        return super().get_queryset()
```

### 3. Context Middleware

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

### 4. View Mixin

```python
class CompanyFilterMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        company = get_current_company()
        if company and hasattr(qs.model, 'company'):
            return qs.filter(company=company)
        return qs
```

## Critical Validations

Never rely solely on filtering. Add explicit validations:

```python
def create_sale(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        company=request.user.profile.company  # Explicit validation
    )
    # ...
```

## Results

With this pattern, ERP Market handles multiple companies with:

- **0 data leaks** between tenants
- **Simple queries** without complex JOINs
- **Single migrations** for all tenants
- **Centralized backup** of the entire platform

## Conclusion

Row-based multi-tenancy is ideal for SaaS where infrastructure cost matters. The key is being **paranoid** with validations and never assuming that automatic filtering is enough.
