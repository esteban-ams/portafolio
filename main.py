from fasthtml.common import *
from starlette.responses import FileResponse, Response
from pathlib import Path

from components.layout import Page, Navbar
from components.hero import Hero
from components.experience import Experience
from components.skills import Skills
from components.projects import Projects
from components.about import About
from components.blog import BlogSection
from components.contact import Contact
from components.footer import Footer
from data.content import site_config

# Get the absolute path to the static folder
STATIC_PATH = Path(__file__).resolve().parent / 'static'

app, rt = fast_app(
    pico=False,
    debug=True
)

# Explicit route for static files
@rt('/static/{path:path}')
async def get(path: str):
    file_path = STATIC_PATH / path
    if file_path.exists():
        return FileResponse(file_path)
    return Response('Not found', status_code=404)

@rt('/')
def get():
    return Page(
        Navbar(),
        Hero(),
        Experience(),
        Skills(),
        Projects(),
        About(),
        BlogSection(),
        Contact(),
        Footer(),
        title=site_config['title']
    )

# Blog routes
@rt('/blog')
def get():
    from pages.blog import blog_list
    return blog_list()

@rt('/blog/{slug}')
def get(slug: str):
    from pages.blog import blog_post
    return blog_post(slug)

# Contact form handler
@rt('/contact')
async def post(name: str, email: str, message: str):
    # Here you would handle the contact form submission
    # For now, return a success message via HTMX
    return Div(
        P('¡Gracias por contactarme! Te responderé pronto.', cls='success-message'),
        id='contact-form-response'
    )

serve()
