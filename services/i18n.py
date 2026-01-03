"""
Internationalization (i18n) service.

Simple custom implementation for translation handling.
"""

import yaml
from pathlib import Path
from contextvars import ContextVar
from functools import reduce

# Context variable to store current language per request
current_language: ContextVar[str] = ContextVar('current_language', default='es')

# Supported languages
SUPPORTED_LANGUAGES = ['es', 'en']
DEFAULT_LANGUAGE = 'es'

# Locales path
LOCALES_PATH = Path(__file__).resolve().parent.parent / 'locales'

# Cache for loaded translations
_translations_cache: dict = {}


def _load_translations(lang: str) -> dict:
    """Load translations for a language from YAML file."""
    if lang in _translations_cache:
        return _translations_cache[lang]

    file_path = LOCALES_PATH / f'{lang}.yml'
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            _translations_cache[lang] = yaml.safe_load(f) or {}
    else:
        _translations_cache[lang] = {}

    return _translations_cache[lang]


def get_language() -> str:
    """Get current language from context."""
    return current_language.get()


def set_language(lang: str) -> None:
    """Set current language in context."""
    if lang in SUPPORTED_LANGUAGES:
        current_language.set(lang)


def t(key: str, **kwargs) -> str:
    """
    Translate a key using current language.

    Usage:
        t('nav.home')  # Returns "Inicio" or "Home"
        t('hero.greeting')  # Returns "Hola, soy" or "Hi, I'm"
    """
    lang = get_language()
    translations = _load_translations(lang)

    # Navigate nested dict using dot notation
    try:
        value = reduce(lambda d, k: d[k], key.split('.'), translations)
        # Handle string interpolation if kwargs provided
        if kwargs and isinstance(value, str):
            return value.format(**kwargs)
        return value
    except (KeyError, TypeError):
        # Fallback to default language
        if lang != DEFAULT_LANGUAGE:
            fallback_translations = _load_translations(DEFAULT_LANGUAGE)
            try:
                value = reduce(lambda d, k: d[k], key.split('.'), fallback_translations)
                if kwargs and isinstance(value, str):
                    return value.format(**kwargs)
                return value
            except (KeyError, TypeError):
                pass
        # Return key if translation not found
        return key


def detect_language_from_header(accept_language: str | None) -> str:
    """
    Detect preferred language from Accept-Language header.

    Examples:
        "en-US,en;q=0.9,es;q=0.8" -> "en"
        "es-ES,es;q=0.9" -> "es"
        None -> "es" (default)
    """
    if not accept_language:
        return DEFAULT_LANGUAGE

    # Parse Accept-Language header
    languages = []
    for part in accept_language.split(','):
        part = part.strip()
        if ';' in part:
            lang, q = part.split(';')
            q = float(q.split('=')[1]) if '=' in q else 1.0
        else:
            lang = part
            q = 1.0

        # Extract base language (e.g., "en-US" -> "en")
        base_lang = lang.split('-')[0].lower()
        if base_lang in SUPPORTED_LANGUAGES:
            languages.append((base_lang, q))

    # Sort by quality and return best match
    if languages:
        languages.sort(key=lambda x: x[1], reverse=True)
        return languages[0][0]

    return DEFAULT_LANGUAGE


def get_content_path(base_path: str, lang: str = None) -> Path:
    """
    Get language-specific content path.

    Usage:
        get_content_path('blog')  # Returns Path to content/{lang}/blog
        get_content_path('projects', 'en')  # Returns Path to content/en/projects
    """
    if lang is None:
        lang = get_language()

    content_base = Path(__file__).resolve().parent.parent / 'content'
    return content_base / lang / base_path
