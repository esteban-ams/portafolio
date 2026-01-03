"""
Blog post loader from Markdown files.

Supports nested folder structure for organization:

content/{lang}/blog/
├── fasthtml/
│   ├── introduction.md
│   ├── deployment.md
│   └── production-ready.md
├── python/
│   └── decorators.md
└── standalone-post.md

Each .md file has YAML frontmatter:

---
title: My Post Title
slug: my-post-title        # Optional: defaults to filename
date: 2024-01-15
tags: [Python, FastHTML]
excerpt: A short description of the post.
category: FastHTML         # Optional: defaults to folder name
---

# Post content here in Markdown...
"""

import re
import frontmatter
import markdown
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache
from textwrap import dedent

# Base content path
CONTENT_DIR = Path(__file__).resolve().parent.parent / 'content'


def get_blog_dir(lang: str = 'es') -> Path:
    """Get blog directory for specified language."""
    return CONTENT_DIR / lang / 'blog'


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


def load_post(filepath: Path, lang: str = 'es') -> Optional[Dict]:
    """Load a single blog post from a markdown file."""
    try:
        post = frontmatter.load(filepath)

        # Process markdown content
        md = get_markdown_processor()
        html_content = md.convert(post.content)

        # Remove first h1 to avoid duplication with page title
        html_content = strip_first_h1(html_content)

        # Determine category from folder structure
        blog_dir = get_blog_dir(lang)
        relative_path = filepath.relative_to(blog_dir)
        if len(relative_path.parts) > 1:
            # File is in a subfolder: blog/category/post.md
            folder_category = relative_path.parts[0].replace('-', ' ').title()
        else:
            # File is in root: blog/post.md
            folder_category = None

        return {
            'slug': post.get('slug', filepath.stem),
            'title': post.get('title', 'Untitled'),
            'date': str(post.get('date', '')),
            'tags': post.get('tags', []),
            'excerpt': post.get('excerpt', ''),
            'category': post.get('category', folder_category),
            'content': post.content,  # Raw markdown
            'html': html_content,      # Rendered HTML
            'filepath': str(filepath),
            'lang': lang,
        }
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def get_all_posts(lang: str = None, refresh: bool = False) -> List[Dict]:
    """
    Get all blog posts sorted by date (newest first).

    Args:
        lang: Language code ('es', 'en'). If None, uses current language.
        refresh: If True, bypass cache and reload from disk.
    """
    if lang is None:
        from services.i18n import get_language
        lang = get_language()

    if refresh:
        _get_posts_cached.cache_clear()
    return _get_posts_cached(lang)


@lru_cache(maxsize=4)
def _get_posts_cached(lang: str) -> List[Dict]:
    """Cached version of post loading (per language)."""
    posts = []
    blog_dir = get_blog_dir(lang)
    print(f"[blog_loader] Loading posts for lang={lang} from {blog_dir}")

    if not blog_dir.exists():
        blog_dir.mkdir(parents=True, exist_ok=True)
        return posts

    # Recursively find all .md files in blog directory and subdirectories
    for filepath in blog_dir.rglob('*.md'):
        post = load_post(filepath, lang)
        if post:
            posts.append(post)

    # Sort by date, newest first
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def get_post_by_slug(slug: str, lang: str = None) -> Optional[Dict]:
    """Get a single post by its slug."""
    posts = get_all_posts(lang)
    return next((p for p in posts if p['slug'] == slug), None)


def render_markdown(content: str) -> str:
    """Render markdown content to HTML."""
    md = get_markdown_processor()
    return md.convert(dedent(content).strip())


# For backwards compatibility with existing code
def get_blog_posts() -> List[Dict]:
    """Alias for get_all_posts for backwards compatibility."""
    return get_all_posts()


def clear_blog_cache():
    """Clear the blog posts cache (useful for development)."""
    _get_posts_cached.cache_clear()
    print("[blog_loader] Cache cleared")


# Clear cache on module load to ensure fresh data on server restart
clear_blog_cache()
