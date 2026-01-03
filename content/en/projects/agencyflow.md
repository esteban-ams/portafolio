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
excerpt: Multi-tenant SaaS platform for marketing agencies. Complete CRM with pipelines, automation system (triggers + actions), lead capture, and appointment scheduling. Hypermedia-driven architecture with HTMX.
---

# AgencyFlow

All-in-one SaaS platform for digital marketing agencies. Combines CRM, automations, lead capture, and calendar in a single tool with multi-tenant architecture.

## The Problem

Small and medium marketing agencies use multiple disconnected tools:
- HubSpot or Pipedrive for CRM
- Calendly for appointments
- Zapier for automations
- Typeform for forms

This generates:
- High costs ($200+/month per tool)
- Fragmented data
- Fragile integrations
- Multiple learning curves

## Solution

AgencyFlow unifies everything in a platform with:

### Visual Pipeline CRM

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline: New Clients                                       │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  Initial    │  Proposal   │  Negotiation│  Closed         │
│  Contact    │  Sent       │             │                 │
├─────────────┼─────────────┼─────────────┼─────────────────┤
│ [Lead 1]    │ [Lead 3]    │ [Lead 5]    │ [Lead 7]        │
│ [Lead 2]    │ [Lead 4]    │             │ [Lead 8]        │
│             │             │             │ [Lead 9]        │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

Drag & drop to move leads between stages, with real-time updates via HTMX.

### Automation System

Automation engine based on triggers and actions:

```python
# Automation model
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

**Available Triggers:**
| Trigger | Description |
|---------|-------------|
| `lead_created` | When a new lead is created |
| `stage_changed` | When a lead changes stage |
| `form_submitted` | When a form is submitted |
| `appointment_booked` | When an appointment is scheduled |
| `tag_added` | When a tag is added to the lead |

**Available Actions:**
- Send email
- Send SMS (via Twilio)
- Add tag
- Move to stage
- Create task
- Notify team
- External webhook

### Lead Capture

Embeddable forms with customizable design:

```html
<!-- Embed code -->
<script src="https://agencyflow.app/embed.js"></script>
<div data-af-form="abc123"></div>
```

Forms:
- Adapt to site style
- Automatically capture UTM parameters
- Real-time validation
- Trigger automations on submit

### Appointment Calendar

Integrated scheduling system:

```python
@rt('/book/{calendar_slug}')
def booking_page(calendar_slug: str):
    calendar = get_calendar_by_slug(calendar_slug)

    # Get availability
    available_slots = get_available_slots(
        calendar=calendar,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14)
    )

    return BookingForm(calendar, available_slots)

@rt('/book/{calendar_slug}')
async def post(calendar_slug: str, slot: str, name: str, email: str):
    # Create appointment
    appointment = create_appointment(calendar_slug, slot, name, email)

    # Trigger automation
    trigger_automation('appointment_booked', {
        'appointment': appointment,
        'lead': get_or_create_lead(email, name)
    })

    return BookingConfirmation(appointment)
```

## Hypermedia Architecture

AgencyFlow uses HTMX for a SPA-like experience without heavy JavaScript:

```python
# Pipeline drag & drop
@rt('/leads/{lead_id}/move')
async def post(lead_id: int, stage_id: int):
    lead = move_lead_to_stage(lead_id, stage_id)

    # Trigger automation
    trigger_automation('stage_changed', {
        'lead': lead,
        'new_stage': stage_id
    })

    # Return only the updated card
    return LeadCard(lead)
```

```html
<!-- Frontend with HTMX -->
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

Each agency has its completely isolated space:

```python
class CompanyMiddleware:
    def __call__(self, request):
        # Detect company by subdomain
        host = request.headers.get('host', '')
        subdomain = host.split('.')[0]

        if subdomain and subdomain != 'www':
            request.company = Company.objects.get(subdomain=subdomain)
        elif request.user.is_authenticated:
            request.company = request.user.company

        return self.get_response(request)
```

## Tech Stack

- **Framework**: FastHTML (Python)
- **Interactivity**: HTMX + Alpine.js
- **Database**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Email**: SendGrid
- **SMS**: Twilio

## Metrics

- **50+** agencies in private beta
- **10,000+** leads processed
- **5,000+** automations executed
- **99.5%** uptime

## Next Steps

- Facebook Leads integration
- Analytics dashboard
- Mobile app for notifications
- White-label for large agencies
