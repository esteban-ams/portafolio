from fasthtml.common import *
from data.content import about_content

def About():
    """About section with personal story."""
    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Sobre mí', cls='section-label'),
                H2('Conóceme', cls='section-title'),
                cls='section-header'
            ),

            # About content
            Div(
                # Text content
                Div(
                    P(about_content['intro'], cls='about-intro'),
                    *[P(paragraph, cls='about-paragraph') for paragraph in about_content['paragraphs']],

                    # Fun facts or interests (optional)
                    Div(
                        H4('Cuando no estoy programando...', cls='about-subtitle'),
                        Ul(
                            Li('Contribuyo a proyectos open source'),
                            Li('Escribo artículos técnicos'),
                            Li('Aprendo nuevas tecnologías'),
                            Li('Disfruto del café y la música'),
                            cls='about-list'
                        ),
                        cls='about-interests'
                    ),

                    cls='about-text'
                ),

                # Image
                Div(
                    Div(
                        Img(src=about_content['image'], alt='Foto personal', loading='lazy') if about_content.get('image') else Div(cls='about-image-placeholder'),
                        cls='about-image-wrapper'
                    ),
                    cls='about-image-container'
                ),

                cls='about-content'
            ),

            cls='container'
        ),
        id='about',
        cls='about-section section',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }"}
    )
