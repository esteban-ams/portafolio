from fasthtml.common import *
from data.content import hero_content, site_config

def Hero():
    """Hero section with animated introduction."""
    return ft_hx('section',
        Div(
            # Animated greeting
            Div(
                Span(hero_content['greeting'], cls='hero-greeting'),
                H1(hero_content['name'], cls='hero-name'),
                cls='hero-intro',
                **{'x-data': '{ show: false }',
                   'x-init': 'setTimeout(() => show = true, 100)',
                   'x-show': 'show',
                   'x-transition:enter': 'transition ease-out duration-700',
                   'x-transition:enter-start': 'opacity-0 transform translate-y-4',
                   'x-transition:enter-end': 'opacity-100 transform translate-y-0'}
            ),

            # Tagline with typing effect
            H2(hero_content['tagline'], cls='hero-tagline',
               **{'x-data': '{ show: false }',
                  'x-init': 'setTimeout(() => show = true, 400)',
                  'x-show': 'show',
                  'x-transition:enter': 'transition ease-out duration-700',
                  'x-transition:enter-start': 'opacity-0',
                  'x-transition:enter-end': 'opacity-100'}
            ),

            # Description
            P(hero_content['description'], cls='hero-description',
              **{'x-data': '{ show: false }',
                 'x-init': 'setTimeout(() => show = true, 700)',
                 'x-show': 'show',
                 'x-transition:enter': 'transition ease-out duration-700',
                 'x-transition:enter-start': 'opacity-0',
                 'x-transition:enter-end': 'opacity-100'}
            ),

            # CTA Buttons
            Div(
                A(hero_content['cta_primary'], href='/#projects', cls='btn btn-primary'),
                A(hero_content['cta_secondary'], href='/#contact', cls='btn btn-secondary'),
                cls='hero-cta',
                **{'x-data': '{ show: false }',
                   'x-init': 'setTimeout(() => show = true, 1000)',
                   'x-show': 'show',
                   'x-transition:enter': 'transition ease-out duration-500',
                   'x-transition:enter-start': 'opacity-0 transform translate-y-4',
                   'x-transition:enter-end': 'opacity-100 transform translate-y-0'}
            ),

            # Social links
            Div(
                A(
                    Span('GitHub', cls='sr-only'),
                    SvgIcon('github'),
                    href=site_config['github'],
                    target='_blank',
                    rel='noopener',
                    cls='social-link'
                ),
                A(
                    Span('LinkedIn', cls='sr-only'),
                    SvgIcon('linkedin'),
                    href=site_config['linkedin'],
                    target='_blank',
                    rel='noopener',
                    cls='social-link'
                ),
                cls='hero-social'
            ),

            cls='hero-content container'
        ),

        # Scroll indicator
        Div(
            A(
                Span('Scroll', cls='scroll-text'),
                Div(cls='scroll-arrow'),
                href='/#experience',
                cls='scroll-indicator'
            ),
            cls='hero-scroll'
        ),

        id='hero',
        cls='hero-section'
    )

def SvgIcon(name):
    """Return SVG icon by name."""
    icons = {
        'github': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>',
        'linkedin': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>',
        'twitter': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path></svg>',
        'email': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>',
        'external': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>',
        'arrow-right': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>',
    }
    return NotStr(icons.get(name, ''))
