from fasthtml.common import *  # pyright: ignore[reportMissingImports]
from data.blog_loader import get_all_posts

def BlogSection():
    """Blog section with recent posts preview."""
    recent_posts = get_all_posts()[:3]  # Show only 3 most recent

    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Blog', cls='section-label'),
                H2('Artículos Recientes', cls='section-title'),
                cls='section-header'
            ),

            # Blog posts grid
            Div(
                *[BlogCard(post, idx) for idx, post in enumerate(recent_posts)],
                cls='blog-grid'
            ),

            # View all link
            Div(
                A('Ver todos los artículos', href='/blog', cls='btn btn-outline'),
                cls='blog-view-all'
            ),

            cls='container'
        ),
        id='blog',
        cls='blog-section section'
    )

def BlogCard(post, idx):
    """Blog post card for homepage."""
    return Article(
        # Date
        Time(post['date'], datetime=post['date'], cls='blog-card-date'),

        # Title
        H3(
            A(post['title'], href=f"/blog/{post['slug']}", cls='blog-card-title-link'),
            cls='blog-card-title'
        ),

        # Excerpt
        P(post['excerpt'], cls='blog-card-excerpt'),

        # Tags
        Div(
            *[Span(tag, cls='blog-tag') for tag in post.get('tags', [])[:3]],
            cls='blog-card-tags'
        ),

        # Read more
        A(
            'Leer más',
            NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'),
            href=f"/blog/{post['slug']}",
            cls='blog-card-link'
        ),

        cls='blog-card',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }",
           'style': f'--delay: {idx * 100}ms'}
    )

def BlogListCard(post):
    """Blog post card for blog list page."""
    return Article(
        Div(
            # Date and reading time
            Div(
                Time(post['date'], datetime=post['date']),
                Span('·', cls='separator'),
                Span('5 min lectura', cls='reading-time'),
                cls='blog-list-meta'
            ),

            # Title
            H2(
                A(post['title'], href=f"/blog/{post['slug']}"),
                cls='blog-list-title'
            ),

            # Excerpt
            P(post['excerpt'], cls='blog-list-excerpt'),

            # Tags
            Div(
                *[Span(tag, cls='blog-tag') for tag in post.get('tags', [])],
                cls='blog-list-tags'
            ),

            cls='blog-list-content'
        ),

        cls='blog-list-card'
    )
