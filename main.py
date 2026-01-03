from fasthtml.common import *
from starlette.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Production settings
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 5001))

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
from services.i18n import set_language, detect_language_from_header, get_language, SUPPORTED_LANGUAGES

# Get the absolute path to the static folder
STATIC_PATH = Path(__file__).resolve().parent / 'static'

app, rt = fast_app(
    pico=False,
    debug=DEBUG
)


# Language detection middleware
class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Priority: 1) ?lang= param, 2) cookie, 3) Accept-Language header
        lang = request.query_params.get('lang')

        if not lang or lang not in SUPPORTED_LANGUAGES:
            lang = request.cookies.get('lang')

        if not lang or lang not in SUPPORTED_LANGUAGES:
            accept_lang = request.headers.get('accept-language')
            lang = detect_language_from_header(accept_lang)

        set_language(lang)

        response = await call_next(request)

        # Set cookie if lang was specified in query param
        if request.query_params.get('lang') in SUPPORTED_LANGUAGES:
            response.set_cookie('lang', lang, max_age=60*60*24*365)  # 1 year

        return response


app.add_middleware(LanguageMiddleware)

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

# Project routes
@rt('/projects')
def get():
    from pages.projects import projects_list
    return projects_list()

@rt('/projects/{slug}')
def get(slug: str):
    from pages.projects import project_detail
    return project_detail(slug)

# Contact form handler
@rt('/contact')
async def post(name: str, email: str, message: str):
    from services.email import send_contact_email, ContactMessage
    from services.i18n import t

    # Basic validation
    if not name or not email or not message:
        return Div(
            P(t('contact.error_fields'), cls='error-message'),
            id='contact-form-response'
        )

    # Send email
    msg = ContactMessage(name=name.strip(), email=email.strip(), message=message.strip())
    success, error = send_contact_email(msg)

    if success:
        return Div(
            P(t('contact.success'), cls='success-message'),
            id='contact-form-response'
        )
    else:
        # Log error but show friendly message
        print(f"Email error: {error}")
        return Div(
            P(t('contact.error'), cls='error-message'),
            id='contact-form-response'
        )

if __name__ == "__main__":
    serve(host='0.0.0.0', port=PORT, reload=DEBUG)
