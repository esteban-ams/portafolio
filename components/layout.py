from fasthtml.common import *
from data.content import site_config

def Page(*children, title=None):
    """Main page wrapper with HTML structure.

    Args:
        *children: Page content components
        title: Page title
    """
    return Html(
        Head(
            Title(title or site_config['title']),
            Meta(charset='utf-8'),
            Meta(name='viewport', content='width=device-width, initial-scale=1'),
            Meta(name='description', content=site_config['description']),
            # Google Fonts - Geometric Bold Theme
            Link(rel='preconnect', href='https://fonts.googleapis.com'),
            Link(rel='preconnect', href='https://fonts.gstatic.com', crossorigin=True),
            Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap'),
            # CSS
            Link(rel='stylesheet', href='/static/css/main.css'),
            Link(rel='stylesheet', href='/static/css/theme-geometric.css'),
            # Alpine.js
            Script(src='https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js', defer=True),
        ),
        Body(
            *children,
            cls='page'
        ),
        lang='es',
        **{'data-theme': 'geometric'}
    )

def Navbar():
    """Fixed navigation bar with smooth scroll links."""
    nav_items = [
        ('Inicio', '#hero'),
        ('Experiencia', '#experience'),
        ('Skills', '#skills'),
        ('Proyectos', '#projects'),
        ('Sobre mí', '#about'),
        ('Blog', '#blog'),
        ('Contacto', '#contact'),
    ]

    return Nav(
        Div(
            A(site_config['name'].split()[0], href='/', cls='nav-logo'),
            Div(
                *[A(name, href=href, cls='nav-link') for name, href in nav_items],
                cls='nav-links',
                **{'x-data': '{ open: false }'}
            ),
            Button(
                Span(cls='hamburger-line'),
                Span(cls='hamburger-line'),
                Span(cls='hamburger-line'),
                cls='hamburger',
                **{'@click': 'open = !open', 'x-show': 'window.innerWidth < 768'}
            ),
            cls='nav-container'
        ),
        cls='navbar',
        **{'x-data': '{ scrolled: false }',
           'x-init': "window.addEventListener('scroll', () => { scrolled = window.scrollY > 50 })",
           ':class': "{ 'scrolled': scrolled }"}
    )

def Section(*children, id=None, cls='section'):
    """Standard section wrapper."""
    return Section_tag(
        Div(*children, cls='container'),
        id=id,
        cls=cls
    )

def Section_tag(*children, **kwargs):
    """HTML section element."""
    return ft_hx('section', *children, **kwargs)

def Container(*children, cls='container'):
    """Container wrapper for centered content."""
    return Div(*children, cls=cls)
