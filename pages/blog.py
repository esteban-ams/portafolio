from fasthtml.common import *
from components.layout import Page, Navbar
from components.footer import Footer
from components.blog import BlogListCard
from data.content import site_config
from data.blog_loader import get_all_posts, get_post_by_slug

def blog_list():
    """Blog listing page."""
    posts = get_all_posts()

    return Page(
        Navbar(),
        ft_hx('main',
            Div(
                # Page header
                Div(
                    H1('Blog', cls='page-title'),
                    P('Artículos sobre desarrollo, tecnología y más.', cls='page-description'),
                    cls='page-header'
                ),

                # Blog posts list
                Div(
                    *[BlogListCard(post) for post in posts],
                    cls='blog-list'
                ),

                cls='container'
            ),
            cls='blog-page'
        ),
        Footer(),
        title=f'Blog | {site_config["name"]}'
    )

def blog_post(slug: str):
    """Individual blog post page."""
    post = get_post_by_slug(slug)

    if not post:
        return Page(
            Navbar(),
            ft_hx('main',
                Div(
                    H1('Artículo no encontrado', cls='page-title'),
                    P('El artículo que buscas no existe.'),
                    A('Volver al blog', href='/blog', cls='btn btn-primary'),
                    cls='container not-found'
                ),
                cls='blog-page'
            ),
            Footer(),
            title=f'No encontrado | {site_config["name"]}'
        )

    return Page(
        Navbar(),
        ft_hx('article',
            Div(
                # Post header
                Div(
                    A('← Volver al blog', href='/blog', cls='back-link'),
                    Time(post['date'], datetime=post['date'], cls='post-date'),
                    H1(post['title'], cls='post-title'),
                    Div(
                        *[Span(tag, cls='blog-tag') for tag in post.get('tags', [])],
                        cls='post-tags'
                    ),
                    cls='post-header'
                ),

                # Post content (pre-rendered HTML from markdown)
                Div(
                    NotStr(post['html']),
                    cls='post-content prose'
                ),

                # Post footer
                Div(
                    A('← Artículo anterior', href='/blog', cls='post-nav-link'),
                    A('Siguiente artículo →', href='/blog', cls='post-nav-link'),
                    cls='post-nav'
                ),

                cls='container post-container'
            ),
            cls='blog-post-page'
        ),
        Footer(),
        title=f'{post["title"]} | {site_config["name"]}'
    )
