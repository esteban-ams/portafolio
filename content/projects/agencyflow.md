---
title: AgencyFlow
slug: agencyflow
technologies:
  - FastHTML
  - PostgreSQL
  - Redis
  - Celery
  - TailwindCSS
github: https://github.com/estebanmartinezsoto/agencyflow
demo: null
featured: true
image: /static/images/agencyflow.jpg
excerpt: Plataforma SaaS multi-tenant para agencias de marketing. CRM completo con pipelines, sistema de automatizaciones (triggers + acciones), captura de leads, y calendario de citas. Arquitectura hypermedia-driven con HTMX.
---

# AgencyFlow

Plataforma SaaS todo-en-uno para agencias de marketing digital. Combina CRM, automatizaciones, captura de leads, y calendario en una sola herramienta con arquitectura multi-tenant.

## El Problema

Las agencias de marketing pequenas y medianas usan multiples herramientas desconectadas:
- HubSpot o Pipedrive para CRM
- Calendly para citas
- Zapier para automatizaciones
- Typeform para formularios

Esto genera:
- Costos elevados ($200+/mes por herramienta)
- Datos fragmentados
- Integraciones fragiles
- Curva de aprendizaje multiple

## Solucion

AgencyFlow unifica todo en una plataforma con:

### CRM con Pipelines Visuales

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline: Nuevos Clientes                                  │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  Contacto   │  Propuesta  │  Negociacion│  Cerrado        │
│  Inicial    │  Enviada    │             │                 │
├─────────────┼─────────────┼─────────────┼─────────────────┤
│ [Lead 1]    │ [Lead 3]    │ [Lead 5]    │ [Lead 7]        │
│ [Lead 2]    │ [Lead 4]    │             │ [Lead 8]        │
│             │             │             │ [Lead 9]        │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

Drag & drop para mover leads entre etapas, con actualizacion en tiempo real via HTMX.

### Sistema de Automatizaciones

Motor de automatizaciones basado en triggers y acciones:

```python
# Modelo de automatizacion
class Automation(CompanyBoundModel):
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(choices=TRIGGER_TYPES)
    trigger_config = models.JSONField()
    is_active = models.BooleanField(default=True)

class AutomationAction(models.Model):
    automation = models.ForeignKey(Automation, related_name='actions')
    action_type = models.CharField(choices=ACTION_TYPES)
    action_config = models.JSONField()
    order = models.IntegerField()
    delay_minutes = models.IntegerField(default=0)
```

**Triggers disponibles:**
| Trigger | Descripcion |
|---------|-------------|
| `lead_created` | Cuando se crea un nuevo lead |
| `stage_changed` | Cuando un lead cambia de etapa |
| `form_submitted` | Cuando se envia un formulario |
| `appointment_booked` | Cuando se agenda una cita |
| `tag_added` | Cuando se agrega un tag al lead |

**Acciones disponibles:**
- Enviar email
- Enviar SMS (via Twilio)
- Agregar tag
- Mover a etapa
- Crear tarea
- Notificar al equipo
- Webhook externo

### Captura de Leads

Formularios embebibles con diseno personalizable:

```html
<!-- Codigo para embed -->
<script src="https://agencyflow.app/embed.js"></script>
<div data-af-form="abc123"></div>
```

Los formularios:
- Se adaptan al estilo del sitio
- Capturan UTM parameters automaticamente
- Validan en tiempo real
- Disparan automatizaciones al enviar

### Calendario de Citas

Sistema de agendamiento integrado:

```python
@rt('/book/{calendar_slug}')
def booking_page(calendar_slug: str):
    calendar = get_calendar_by_slug(calendar_slug)

    # Obtener disponibilidad
    available_slots = get_available_slots(
        calendar=calendar,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14)
    )

    return BookingForm(calendar, available_slots)

@rt('/book/{calendar_slug}')
async def post(calendar_slug: str, slot: str, name: str, email: str):
    # Crear cita
    appointment = create_appointment(calendar_slug, slot, name, email)

    # Disparar automatizacion
    trigger_automation('appointment_booked', {
        'appointment': appointment,
        'lead': get_or_create_lead(email, name)
    })

    return BookingConfirmation(appointment)
```

## Arquitectura Hypermedia

AgencyFlow usa HTMX para una experiencia SPA-like sin JavaScript pesado:

```python
# Drag & drop en pipeline
@rt('/leads/{lead_id}/move')
async def post(lead_id: int, stage_id: int):
    lead = move_lead_to_stage(lead_id, stage_id)

    # Disparar automatizacion
    trigger_automation('stage_changed', {
        'lead': lead,
        'new_stage': stage_id
    })

    # Retornar solo la tarjeta actualizada
    return LeadCard(lead)
```

```html
<!-- Frontend con HTMX -->
<div class="lead-card"
     draggable="true"
     hx-post="/leads/123/move"
     hx-vals='{"stage_id": "target_stage"}'
     hx-target="this"
     hx-swap="outerHTML">
    ...
</div>
```

## Multi-Tenancy

Cada agencia tiene su espacio completamente aislado:

```python
class CompanyMiddleware:
    def __call__(self, request):
        # Detectar empresa por subdominio
        host = request.headers.get('host', '')
        subdomain = host.split('.')[0]

        if subdomain and subdomain != 'www':
            request.company = Company.objects.get(subdomain=subdomain)
        elif request.user.is_authenticated:
            request.company = request.user.company

        return self.get_response(request)
```

## Stack Tecnico

- **Framework**: FastHTML (Python)
- **Interactividad**: HTMX + Alpine.js
- **Base de datos**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Email**: SendGrid
- **SMS**: Twilio

## Metricas

- **50+** agencias en beta privada
- **10,000+** leads procesados
- **5,000+** automatizaciones ejecutadas
- **99.5%** uptime

## Proximos Pasos

- Integracion con Facebook Leads
- Dashboard de analytics
- App movil para notificaciones
- White-label para agencias grandes
