from fasthtml.common import *
from data.project_loader import get_all_projects, get_featured_projects

def Projects():
    """Projects showcase section."""
    all_projects = get_all_projects()
    featured = [p for p in all_projects if p.get('featured')]
    other = [p for p in all_projects if not p.get('featured')]

    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Portfolio', cls='section-label'),
                H2('Proyectos Destacados', cls='section-title'),
                cls='section-header'
            ),

            # Featured projects
            Div(
                *[FeaturedProject(project, idx) for idx, project in enumerate(featured)],
                cls='featured-projects'
            ),

            # Other projects (if any)
            Div(
                H3('Otros Proyectos', cls='other-projects-title') if other else '',
                Div(
                    *[ProjectCard(project, idx) for idx, project in enumerate(other)],
                    cls='projects-grid'
                ) if other else '',
                cls='other-projects-section'
            ) if other else '',

            cls='container'
        ),
        id='projects',
        cls='projects-section section'
    )

def FeaturedProject(project, idx):
    """Featured project with large image and details."""
    is_even = idx % 2 == 0

    return Div(
        # Project image
        Div(
            Div(
                Img(src=project['image'], alt=project['title'], loading='lazy') if project.get('image') else '',
                Div(cls='project-image-overlay'),
                cls='project-image-wrapper'
            ),
            cls='featured-project-image'
        ),

        # Project content
        Div(
            Span('Proyecto Destacado', cls='project-label'),
            H3(project['title'], cls='project-title'),
            Div(
                P(project['excerpt']),
                cls='project-description'
            ),

            # Technologies
            Div(
                *[Span(tech, cls='tech-tag') for tech in project['technologies']],
                cls='project-tech'
            ),

            # Links
            Div(
                A(
                    'Ver detalles →',
                    href=f'/projects/{project["slug"]}',
                    cls='project-link project-details-link'
                ),
                A(
                    NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>'),
                    href=project['github'],
                    target='_blank',
                    rel='noopener',
                    cls='project-link',
                    title='Ver código'
                ) if project.get('github') else '',
                A(
                    NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'),
                    href=project['demo'],
                    target='_blank',
                    rel='noopener',
                    cls='project-link',
                    title='Ver demo'
                ) if project.get('demo') else '',
                cls='project-links'
            ),

            cls='featured-project-content'
        ),

        cls=f'featured-project {"featured-project-reverse" if not is_even else ""}',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }"}
    )

def ProjectCard(project, idx):
    """Clean, minimal project card for grid layout."""
    return Div(
        # Gold accent bar at top
        Div(cls='mini-card-accent'),

        # Card inner content
        Div(
            # Header: Title + GitHub link
            Div(
                H4(project['title'], cls='mini-card-title'),
                A(
                    NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>'),
                    href=project['github'],
                    target='_blank',
                    rel='noopener',
                    cls='mini-card-github'
                ) if project.get('github') else None,
                cls='mini-card-header'
            ),

            # Description
            P(project['excerpt'], cls='mini-card-desc'),

            # Footer: Tech tags + Link
            Div(
                Div(
                    *[Span(tech, cls='mini-card-tag') for tech in project['technologies'][:4]],
                    cls='mini-card-tags'
                ),
                A('Ver más →', href=f'/projects/{project["slug"]}', cls='mini-card-link'),
                cls='mini-card-footer'
            ),

            cls='mini-card-body'
        ),

        cls='mini-project-card',
        style=f'--card-delay: {idx * 0.1}s'
    )
