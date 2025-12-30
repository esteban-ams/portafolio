from fasthtml.common import *
from data.content import site_config

def Contact():
    """Contact section with form."""
    return ft_hx('section',
        Div(
            # Section header
            Div(
                Span('Contacto', cls='section-label'),
                H2('Hablemos', cls='section-title'),
                P('¿Tienes un proyecto en mente o simplemente quieres saludar? Mi bandeja de entrada está siempre abierta.', cls='section-description'),
                cls='section-header'
            ),

            # Contact content
            Div(
                # Contact form
                Div(
                    Form(
                        # Name field
                        Div(
                            Label('Nombre', fr='name', cls='form-label'),
                            Input(
                                type='text',
                                id='name',
                                name='name',
                                required=True,
                                placeholder='Tu nombre',
                                cls='form-input'
                            ),
                            cls='form-group'
                        ),

                        # Email field
                        Div(
                            Label('Email', fr='email', cls='form-label'),
                            Input(
                                type='email',
                                id='email',
                                name='email',
                                required=True,
                                placeholder='tu@email.com',
                                cls='form-input'
                            ),
                            cls='form-group'
                        ),

                        # Message field
                        Div(
                            Label('Mensaje', fr='message', cls='form-label'),
                            Textarea(
                                id='message',
                                name='message',
                                required=True,
                                rows='5',
                                placeholder='¿En qué puedo ayudarte?',
                                cls='form-textarea'
                            ),
                            cls='form-group'
                        ),

                        # Submit button
                        Button(
                            'Enviar mensaje',
                            NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>'),
                            type='submit',
                            cls='btn btn-primary btn-full'
                        ),

                        # Response area for HTMX
                        Div(id='contact-form-response', cls='form-response'),

                        hx_post='/contact',
                        hx_target='#contact-form-response',
                        hx_swap='innerHTML',
                        cls='contact-form',
                        **{'x-data': '{ sending: false }',
                           '@submit': 'sending = true',
                           'x-on:htmx:after-request': 'sending = false'}
                    ),
                    cls='contact-form-wrapper'
                ),

                # Contact info
                Div(
                    H3('O contáctame directamente', cls='contact-info-title'),

                    # Email
                    A(
                        NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>'),
                        Span(site_config['email']),
                        href=f"mailto:{site_config['email']}",
                        cls='contact-link'
                    ),

                    # Social links
                    Div(
                        A(
                            NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>'),
                            href=site_config['github'],
                            target='_blank',
                            rel='noopener',
                            cls='social-link-large',
                            title='GitHub'
                        ),
                        A(
                            NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>'),
                            href=site_config['linkedin'],
                            target='_blank',
                            rel='noopener',
                            cls='social-link-large',
                            title='LinkedIn'
                        ),
                        A(
                            NotStr('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path></svg>'),
                            href=site_config['twitter'],
                            target='_blank',
                            rel='noopener',
                            cls='social-link-large',
                            title='Twitter'
                        ),
                        cls='contact-social'
                    ),

                    cls='contact-info'
                ),

                cls='contact-content'
            ),

            cls='container'
        ),
        id='contact',
        cls='contact-section section',
        **{'x-data': '{ show: false }',
           'x-intersect': 'show = true',
           ':class': "{ 'visible': show }"}
    )
