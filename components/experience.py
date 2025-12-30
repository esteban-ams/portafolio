from fasthtml.common import *
from data.content import experience_data

def Experience():
    """Experience/Work history section with timeline."""
    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Trayectoria', cls='section-label'),
                H2('Experiencia', cls='section-title'),
                cls='section-header'
            ),

            # Timeline
            Div(
                *[ExperienceCard(exp, idx) for idx, exp in enumerate(experience_data)],
                cls='experience-timeline'
            ),

            cls='container'
        ),
        id='experience',
        cls='experience-section section'
    )

def ExperienceCard(exp, idx):
    """Individual experience card with animation."""
    return Div(
        # Timeline dot
        Div(cls='timeline-dot'),

        # Card content
        Div(
            Div(
                Span(exp['period'], cls='experience-period'),
                H3(exp['role'], cls='experience-role'),
                H4(exp['company'], cls='experience-company'),
                cls='experience-header'
            ),

            P(exp['description'], cls='experience-description'),

            # Highlights
            Ul(
                *[Li(highlight) for highlight in exp['highlights']],
                cls='experience-highlights'
            ),

            # Technologies
            Div(
                *[Span(tech, cls='tech-tag') for tech in exp['technologies']],
                cls='experience-tech'
            ),

            cls='experience-card-content'
        ),

        cls='experience-card',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }"}
    )
