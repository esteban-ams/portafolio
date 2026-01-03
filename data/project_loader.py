"""
Project loader from Markdown files.

Similar to blog posts, projects are stored as markdown files with frontmatter:

content/{lang}/projects/
├── erp-market.md
├── road-report.md
├── agencyflow.md
└── openmedia.md

Each .md file has YAML frontmatter:

---
title: ERP Market
slug: erp-market
technologies: [Django, PostgreSQL, HTMX]
github: https://github.com/user/repo
demo: https://demo.example.com  # Optional
featured: true
image: /static/images/erp-market.jpg  # Optional
excerpt: Short description for cards
---

# Full project description in Markdown...

## Features
- Feature 1
- Feature 2

## Technical Details
...
"""

import re
import frontmatter
import markdown
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache

# Base content path
CONTENT_DIR = Path(__file__).resolve().parent.parent / 'content'


def get_projects_dir(lang: str = 'es') -> Path:
    """Get projects directory for specified language."""
    return CONTENT_DIR / lang / 'projects'


def get_markdown_processor():
    """Create configured markdown processor with extensions."""
    return markdown.Markdown(
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc',
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
            }
        }
    )


def strip_first_h1(html: str) -> str:
    """Remove the first h1 tag from HTML to avoid title duplication."""
    return re.sub(r'^(\s*<h1[^>]*>.*?</h1>\s*)', '', html, count=1, flags=re.DOTALL)


def load_project(filepath: Path, lang: str = 'es') -> Optional[Dict]:
    """Load a single project from a markdown file."""
    try:
        project = frontmatter.load(filepath)

        # Process markdown content
        md = get_markdown_processor()
        html_content = md.convert(project.content)

        # Remove first h1 to avoid duplication with page title
        html_content = strip_first_h1(html_content)

        return {
            'slug': project.get('slug', filepath.stem),
            'title': project.get('title', 'Untitled Project'),
            'description': project.get('excerpt', ''),
            'excerpt': project.get('excerpt', ''),
            'technologies': project.get('technologies', []),
            'github': project.get('github'),
            'demo': project.get('demo'),
            'featured': project.get('featured', False),
            'image': project.get('image', '/static/images/project-default.jpg'),
            'content': project.content,  # Raw markdown
            'html': html_content,         # Rendered HTML
            'filepath': str(filepath),
            'lang': lang,
        }
    except Exception as e:
        print(f"Error loading project {filepath}: {e}")
        return None


def get_all_projects(lang: str = None, refresh: bool = False) -> List[Dict]:
    """
    Get all projects.

    Args:
        lang: Language code ('es', 'en'). If None, uses current language.
        refresh: If True, bypass cache and reload from disk.
    """
    if lang is None:
        from services.i18n import get_language
        lang = get_language()

    if refresh:
        _get_projects_cached.cache_clear()
    return _get_projects_cached(lang)


@lru_cache(maxsize=4)
def _get_projects_cached(lang: str) -> List[Dict]:
    """Cached version of project loading (per language)."""
    projects = []
    projects_dir = get_projects_dir(lang)

    if not projects_dir.exists():
        projects_dir.mkdir(parents=True, exist_ok=True)
        return projects

    # Find all .md files in projects directory
    for filepath in projects_dir.glob('*.md'):
        project = load_project(filepath, lang)
        if project:
            projects.append(project)

    # Sort: featured first, then by title
    projects.sort(key=lambda p: (not p['featured'], p['title']))
    return projects


def get_featured_projects(lang: str = None) -> List[Dict]:
    """Get only featured projects."""
    return [p for p in get_all_projects(lang) if p['featured']]


def get_project_by_slug(slug: str, lang: str = None) -> Optional[Dict]:
    """Get a single project by its slug."""
    projects = get_all_projects(lang)
    return next((p for p in projects if p['slug'] == slug), None)
