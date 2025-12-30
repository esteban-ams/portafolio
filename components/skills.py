from fasthtml.common import *
from data.content import skills_data

def Skills():
    """Skills section with categorized tech stack."""
    categories = [
        ('Lenguajes', 'languages', 'code'),
        ('Frontend', 'frontend', 'layout'),
        ('Backend', 'backend', 'server'),
        ('Herramientas', 'tools', 'tool'),
    ]

    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Habilidades', cls='section-label'),
                H2('Stack Tecnológico', cls='section-title'),
                cls='section-header'
            ),

            # Skills grid
            Div(
                *[SkillCategory(name, skills_data.get(key, []), icon, idx)
                  for idx, (name, key, icon) in enumerate(categories)],
                cls='skills-grid'
            ),

            cls='container'
        ),
        id='skills',
        cls='skills-section section'
    )

def SkillCategory(name, skills, icon, idx):
    """Category card with skill chips."""
    return Div(
        # Category icon and title
        Div(
            SkillIcon(icon),
            H3(name, cls='skill-category-title'),
            cls='skill-category-header'
        ),

        # Skills chips
        Div(
            *[SkillChip(skill) for skill in skills],
            cls='skill-chips'
        ),

        cls='skill-category',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }",
           'style': f'--delay: {idx * 100}ms'}
    )

def SkillChip(skill):
    """Individual skill chip with hover effect."""
    return Span(
        skill,
        cls='skill-chip',
        **{'x-data': '{ hover: false }',
           '@mouseenter': 'hover = true',
           '@mouseleave': 'hover = false',
           ':class': "{ 'active': hover }"}
    )

def SkillIcon(icon_type):
    """Return icon for skill category."""
    icons = {
        'code': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
        'layout': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>',
        'server': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>',
        'tool': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>',
    }
    return NotStr(f'<div class="skill-icon">{icons.get(icon_type, "")}</div>')
