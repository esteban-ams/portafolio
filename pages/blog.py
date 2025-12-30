from fasthtml.common import *
from components.layout import Page, Navbar
from components.footer import Footer
from components.blog import BlogListCard
from data.content import blog_posts, site_config

def blog_list():
    """Blog listing page."""
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
                    *[BlogListCard(post) for post in blog_posts],
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
    post = next((p for p in blog_posts if p['slug'] == slug), None)

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

                # Post content (would be markdown rendered)
                Div(
                    NotStr(render_markdown(post['content'])),
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

def render_markdown(content: str) -> str:
    """Simple markdown rendering (basic implementation)."""
    import re

    # Very basic markdown to HTML conversion
    # In production, use a proper markdown library like markdown or mistune

    html = content

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Code blocks
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', html)

    # Paragraphs
    html = re.sub(r'\n\n(.+?)(?=\n\n|$)', r'<p>\1</p>', html, flags=re.DOTALL)

    return html
