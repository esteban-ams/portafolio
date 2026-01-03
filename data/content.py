# Site configuration and content data
# Edit this file to customize your portfolio

site_config = {
    'title': 'Esteban Martinez | Software Engineer',
    'description': 'Ingeniero en Computacion especializado en arquitectura de software, sistemas distribuidos y soluciones full-stack con Python.',
    'name': 'Esteban Martinez',
    'role': 'Software Engineer',
    'email': 'esteban.ams95@gmail.com',  # TODO: Update with real email
    'github': 'https://github.com/esteban-ams',
    'linkedin': 'https://www.linkedin.com/in/esteban-mart%C3%ADnez-4b1b32137/',
    'twitter': None,
}

hero_content = {
    'greeting': 'Hola, soy',
    'name': site_config['name'],
    'tagline': 'Construyo soluciones que importan.',
    'description': 'Ingeniero en Computacion con experiencia en sistemas empresariales, arquitectura multi-tenant, integraciones complejas y machine learning. Transformo problemas de negocio en software escalable.',
    'cta_primary': 'Ver proyectos',
    'cta_secondary': 'Contactar',
}

experience_data = [
    {
        'company': 'Desarrollo Independiente',
        'role': 'Full-Stack Software Engineer',
        'period': '2022 - Presente',
        'description': 'Diseno y desarrollo de sistemas empresariales completos, desde arquitectura hasta deployment.',
        'highlights': [
            'ERP multi-tenant con integracion SII Chile (facturacion electronica)',
            'Plataforma SaaS para agencias con CRM y automatizaciones',
            'App movil Flutter + FastAPI para reportes ciudadanos',
        ],
        'technologies': ['Python', 'Django', 'FastAPI', 'Flutter', 'PostgreSQL', 'Docker'],
    },
    {
        'company': 'Proyectos de Investigacion',
        'role': 'Machine Learning Engineer',
        'period': '2021 - 2022',
        'description': 'Investigacion en clasificacion multimodal y pipelines de procesamiento de datos.',
        'highlights': [
            'Comparativa de modelos multimodales (CLIP, FLAVA, ViLT)',
            'Pipeline de embeddings con Kafka y pgvector',
            'Sistema de monitoreo de noticias con busqueda semantica',
        ],
        'technologies': ['PyTorch', 'Transformers', 'Kafka', 'pgvector', 'CUDA'],
    },
]

skills_data = {
    'languages': ['Python', 'Dart', 'TypeScript', 'SQL', 'Bash'],
    'frontend': ['Flutter', 'HTMX', 'Alpine.js', 'TailwindCSS', 'FastHTML'],
    'backend': ['Django', 'FastAPI', 'FastHTML', 'Celery', 'SQLAlchemy'],
    'data': ['PostgreSQL', 'Redis', 'Kafka', 'pgvector', 'PyTorch'],
    'devops': ['Docker', 'Git', 'GitHub Actions', 'Linux', 'DigitalOcean'],
}

projects_data = [
    {
        'title': 'ERP Market',
        'description': 'Sistema ERP completo para retail con arquitectura multi-tenant, facturacion electronica SII Chile, POS tactil, gestion de inventario con costeo promedio ponderado, e integracion con impresoras termicas y balanzas digitales.',
        'image': '/static/images/erp-market.jpg',
        'technologies': ['Django', 'PostgreSQL', 'HTMX', 'WeasyPrint', 'Docker'],
        'github': 'https://github.com/estebanmartinezsoto/erp-market-django',
        'demo': None,
        'featured': True,
    },
    {
        'title': 'Road Report',
        'description': 'Aplicacion movil para reportar infracciones de transporte publico. Grabacion de rutas GPS con deteccion de exceso de velocidad, captura de evidencia multimedia, y sistema de validacion inteligente con scoring automatico.',
        'image': '/static/images/road-report.jpg',
        'technologies': ['Flutter', 'FastAPI', 'PostgreSQL', 'Geolocator', 'Riverpod'],
        'github': 'https://github.com/estebanmartinezsoto/road-report',
        'demo': None,
        'featured': True,
    },
    {
        'title': 'AgencyFlow',
        'description': 'Plataforma SaaS multi-tenant para agencias de marketing. CRM completo con pipelines, sistema de automatizaciones (triggers + acciones), captura de leads, y calendario de citas. Arquitectura hypermedia-driven con HTMX.',
        'image': '/static/images/agencyflow.jpg',
        'technologies': ['FastHTML', 'PostgreSQL', 'Redis', 'Celery', 'TailwindCSS'],
        'github': 'https://github.com/estebanmartinezsoto/agencyflow',
        'demo': None,
        'featured': True,
    },
    {
        'title': 'OpenMedia',
        'description': 'Sistema de monitoreo de medios chilenos con crawlers asincrónicos, pipeline Kafka para procesamiento en tiempo real, y busqueda semantica con embeddings vectoriales en pgvector.',
        'image': '/static/images/openmedia.jpg',
        'technologies': ['Python', 'Kafka', 'pgvector', 'Transformers', 'Docker'],
        'github': 'https://github.com/estebanmartinezsoto/openmedia',
        'demo': None,
        'featured': False,
    },
    {
        'title': 'Clasificacion Multimodal',
        'description': 'Proyecto de investigacion comparando modelos de clasificacion texto vs multimodal (BERT, CLIP, FLAVA, ViLT) en multiples datasets. Optimizacion CUDA para entrenamiento a gran escala.',
        'image': '/static/images/ml-research.jpg',
        'technologies': ['PyTorch', 'Transformers', 'CUDA', 'scikit-learn', 'HuggingFace'],
        'github': 'https://github.com/estebanmartinezsoto/multimodal-classification',
        'demo': None,
        'featured': False,
    },
    {
        'title': 'Metalurgica Template',
        'description': 'Template profesional B2B para empresas industriales construido con FastHTML. Diseno "Forja Moderna" con componentes reutilizables, galeria interactiva HTMX, y formularios de contacto/cotizacion.',
        'image': '/static/images/metalurgica.jpg',
        'technologies': ['FastHTML', 'HTMX', 'CSS', 'Alpine.js'],
        'github': 'https://github.com/estebanmartinezsoto/metalurgica-spa',
        'demo': None,
        'featured': False,
    },
]

about_content = {
    'intro': 'Soy desarrollador de software con más de 6 años de experiencia ayudando a negocios a trabajar de forma más inteligente.',
    'paragraphs': [
        '¿Qué significa eso en la práctica? Creo herramientas digitales que te ahorran tiempo y dolores de cabeza:',
        'Sistemas para administrar tu negocio — control de inventario, ventas, clientes, facturación... todo en un solo lugar, accesible desde tu computadora o celular.',
        'Automatización de tareas repetitivas — esas cosas que haces a mano todos los días y te quitan horas que podrías usar en lo que realmente importa.',
        'Aplicaciones a la medida — si tu negocio tiene una necesidad específica que ningún software existente resuelve, lo construimos juntos.',
        'No me interesa venderte tecnología por venderla. Me interesa entender cómo funciona tu negocio y encontrar dónde la tecnología puede hacerte la vida más fácil.',
    ],
    'image': '/static/images/about.jpg',
}

# blog_posts is now loaded from markdown files in content/blog/
# See data/blog_loader.py for the implementation

footer_links = {
    'social': [
        {'name': 'GitHub', 'url': site_config['github'], 'icon': 'github'},
        {'name': 'LinkedIn', 'url': site_config['linkedin'], 'icon': 'linkedin'},
    ],
}
