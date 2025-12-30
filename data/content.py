# Site configuration and content data
# Edit this file to customize your portfolio

site_config = {
    'title': 'Esteban Martinez | Problem Solver',
    'description': 'Ingeniero en Computación especializado en resolver problemas complejos con soluciones de software elegantes.',
    'name': 'Esteban Martinez',
    'role': 'Problem Solver',
    'email': 'esteban@email.com',
    'github': 'https://github.com/estebanmartinez',
    'linkedin': 'https://linkedin.com/in/estebanmartinez',
    'twitter': 'https://twitter.com/estebanmartinez',
}

hero_content = {
    'greeting': 'Hola, soy',
    'name': site_config['name'],
    'tagline': 'Resuelvo problemas con software.',
    'description': 'Ingeniero en Computación apasionado por transformar problemas complejos en soluciones elegantes. No solo escribo código, diseño soluciones.',
    'cta_primary': 'Ver soluciones',
    'cta_secondary': 'Hablemos',
}

experience_data = [
    {
        'company': 'Empresa Ejemplo',
        'role': 'Senior Software Engineer',
        'period': '2022 - Presente',
        'description': 'Liderando el desarrollo de aplicaciones web con Python y TypeScript.',
        'highlights': [
            'Arquitectura de microservicios con FastAPI',
            'Frontend moderno con React/Next.js',
            'CI/CD con GitHub Actions',
        ],
        'technologies': ['Python', 'TypeScript', 'React', 'AWS'],
    },
    {
        'company': 'Otra Empresa',
        'role': 'Software Engineer',
        'period': '2020 - 2022',
        'description': 'Desarrollo full-stack de productos SaaS.',
        'highlights': [
            'Desarrollo de APIs RESTful',
            'Implementación de sistemas de autenticación',
            'Optimización de rendimiento',
        ],
        'technologies': ['Python', 'Django', 'PostgreSQL', 'Docker'],
    },
]

skills_data = {
    'languages': ['Python', 'TypeScript', 'JavaScript', 'Go', 'SQL'],
    'frontend': ['React', 'Next.js', 'HTMX', 'Tailwind CSS', 'Alpine.js'],
    'backend': ['FastAPI', 'FastHTML', 'Django', 'Node.js', 'PostgreSQL'],
    'tools': ['Docker', 'Git', 'AWS', 'GitHub Actions', 'Linux'],
}

projects_data = [
    {
        'title': 'Proyecto Destacado 1',
        'description': 'Una aplicación web moderna que resuelve un problema específico usando tecnologías de vanguardia.',
        'image': '/static/images/project1.jpg',
        'technologies': ['Python', 'FastAPI', 'React', 'PostgreSQL'],
        'github': 'https://github.com/tuusuario/proyecto1',
        'demo': 'https://proyecto1.com',
        'featured': True,
    },
    {
        'title': 'Proyecto Destacado 2',
        'description': 'Sistema de gestión con interfaz intuitiva y arquitectura escalable.',
        'image': '/static/images/project2.jpg',
        'technologies': ['TypeScript', 'Next.js', 'Prisma', 'Vercel'],
        'github': 'https://github.com/tuusuario/proyecto2',
        'demo': 'https://proyecto2.com',
        'featured': True,
    },
    {
        'title': 'Herramienta CLI',
        'description': 'Herramienta de línea de comandos para automatizar tareas de desarrollo.',
        'image': '/static/images/project3.jpg',
        'technologies': ['Python', 'Click', 'Rich'],
        'github': 'https://github.com/tuusuario/cli-tool',
        'demo': None,
        'featured': False,
    },
]

about_content = {
    'intro': 'Ingeniero en Computación con mentalidad de solucionador de problemas.',
    'paragraphs': [
        'Creo firmemente que el mejor código es el que resuelve problemas reales de forma elegante. Mi enfoque va más allá de la programación: analizo, diseño y construyo soluciones que impactan.',
        'Me especializo en entender el problema antes de escribir la primera línea de código. Esta mentalidad me ha permitido crear soluciones eficientes y escalables.',
    ],
    'image': '/static/images/about.jpg',
}

blog_posts = [
    {
        'slug': 'fasthtml-introduccion',
        'title': 'Introducción a FastHTML',
        'excerpt': 'Descubre cómo construir aplicaciones web modernas con Python y FastHTML.',
        'date': '2024-01-15',
        'tags': ['Python', 'FastHTML', 'Web Development'],
        'content': '''
                # Introducción a FastHTML

                FastHTML es un framework moderno para construir aplicaciones web con Python...

                ## Por qué FastHTML

                - Simplicidad
                - Rendimiento
                - Productividad

                ## Ejemplo básico

                ```python
                from fasthtml.common import *
                app, rt = fast_app()

                @rt('/')
                def get():
                    return Div(H1('Hello World!'))

                serve()
                ```
        ''',
    },
]

footer_links = {
    'social': [
        {'name': 'GitHub', 'url': site_config['github'], 'icon': 'github'},
        {'name': 'LinkedIn', 'url': site_config['linkedin'], 'icon': 'linkedin'},
        {'name': 'Twitter', 'url': site_config['twitter'], 'icon': 'twitter'},
    ],
}
