from fasthtml.common import *
from components.layout import Page, Navbar
from components.footer import Footer
from components.hero import SvgIcon
from data.content import site_config
from data.project_loader import get_all_projects, get_project_by_slug


def projects_list():
    """Projects listing page."""
    projects = get_all_projects()

    return Page(
        Navbar(),
        ft_hx('main',
            Div(
                # Page header
                Div(
                    H1('Proyectos', cls='page-title'),
                    P('Sistemas y aplicaciones que he construido.', cls='page-description'),
                    cls='page-header'
                ),

                # Projects grid
                Div(
                    *[ProjectListCard(project) for project in projects],
                    cls='projects-list-grid'
                ),

                cls='container'
            ),
            cls='projects-page'
        ),
        Footer(),
        title=f'Proyectos | {site_config["name"]}'
    )


def ProjectListCard(project):
    """Card for project listing page."""
    return A(
        Div(
            # Image
            Div(
                Img(src=project['image'], alt=project['title'], loading='lazy'),
                cls='project-list-image'
            ),

            # Content
            Div(
                # Tags
                Div(
                    *[Span(tech, cls='tech-tag') for tech in project['technologies'][:4]],
                    cls='project-list-tags'
                ),

                H3(project['title'], cls='project-list-title'),
                P(project['excerpt'], cls='project-list-excerpt'),

                # Featured badge
                Span('Destacado', cls='featured-badge') if project['featured'] else None,

                cls='project-list-content'
            ),

            cls='project-list-card-inner'
        ),
        href=f'/projects/{project["slug"]}',
        cls='project-list-card'
    )


def project_detail(slug: str):
    """Individual project page."""
    project = get_project_by_slug(slug)

    if not project:
        return Page(
            Navbar(),
            ft_hx('main',
                Div(
                    H1('Proyecto no encontrado', cls='page-title'),
                    P('El proyecto que buscas no existe.'),
                    A('Ver todos los proyectos', href='/projects', cls='btn btn-primary'),
                    cls='container not-found'
                ),
                cls='projects-page'
            ),
            Footer(),
            title=f'No encontrado | {site_config["name"]}'
        )

    return Page(
        Navbar(),
        ft_hx('article',
            Div(
                # Project header
                Div(
                    A('← Volver a proyectos', href='/projects', cls='back-link'),

                    # Featured badge
                    Span('Proyecto Destacado', cls='featured-badge-large') if project['featured'] else None,

                    H1(project['title'], cls='project-title'),

                    # Technologies
                    Div(
                        *[Span(tech, cls='tech-tag') for tech in project['technologies']],
                        cls='project-tags'
                    ),

                    # Links
                    Div(
                        A(
                            SvgIcon('github'),
                            'Ver codigo',
                            href=project['github'],
                            target='_blank',
                            rel='noopener',
                            cls='project-link'
                        ) if project['github'] else None,
                        A(
                            SvgIcon('external'),
                            'Ver demo',
                            href=project['demo'],
                            target='_blank',
                            rel='noopener',
                            cls='project-link demo-link'
                        ) if project['demo'] else None,
                        cls='project-links'
                    ),

                    cls='project-header'
                ),

                # Project content (pre-rendered HTML from markdown)
                Div(
                    NotStr(project['html']),
                    cls='project-content prose'
                ),

                # Navigation
                Div(
                    A('← Volver a proyectos', href='/projects', cls='post-nav-link'),
                    A('Ver todos →', href='/#projects', cls='post-nav-link'),
                    cls='post-nav'
                ),

                cls='container project-container'
            ),
            cls='project-detail-page'
        ),
        Footer(),
        title=f'{project["title"]} | {site_config["name"]}'
    )
