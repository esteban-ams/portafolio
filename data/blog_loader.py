"""
Blog post loader from Markdown files.

Supports nested folder structure for organization:

content/blog/
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

# Path to blog content
BLOG_DIR = Path(__file__).resolve().parent.parent / 'content' / 'blog'


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


def load_post(filepath: Path) -> Optional[Dict]:
    """Load a single blog post from a markdown file."""
    try:
        post = frontmatter.load(filepath)

        # Process markdown content
        md = get_markdown_processor()
        html_content = md.convert(post.content)

        # Remove first h1 to avoid duplication with page title
        html_content = strip_first_h1(html_content)

        # Determine category from folder structure
        relative_path = filepath.relative_to(BLOG_DIR)
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
        }
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def get_all_posts(refresh: bool = False) -> List[Dict]:
    """
    Get all blog posts sorted by date (newest first).

    Args:
        refresh: If True, bypass cache and reload from disk.
    """
    if refresh:
        _get_posts_cached.cache_clear()
    return _get_posts_cached()


@lru_cache(maxsize=1)
def _get_posts_cached() -> List[Dict]:
    """Cached version of post loading."""
    posts = []

    if not BLOG_DIR.exists():
        BLOG_DIR.mkdir(parents=True, exist_ok=True)
        return posts

    # Recursively find all .md files in blog directory and subdirectories
    for filepath in BLOG_DIR.rglob('*.md'):
        post = load_post(filepath)
        if post:
            posts.append(post)

    # Sort by date, newest first
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def get_post_by_slug(slug: str) -> Optional[Dict]:
    """Get a single post by its slug."""
    posts = get_all_posts()
    return next((p for p in posts if p['slug'] == slug), None)


def render_markdown(content: str) -> str:
    """Render markdown content to HTML."""
    md = get_markdown_processor()
    return md.convert(dedent(content).strip())


# For backwards compatibility with existing code
def get_blog_posts() -> List[Dict]:
    """Alias for get_all_posts for backwards compatibility."""
    return get_all_posts()
