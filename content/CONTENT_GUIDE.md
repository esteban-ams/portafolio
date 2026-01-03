# Content Guide / Guia de Contenido

This guide explains how to add new content (blog posts and projects) to the portfolio in both languages.

Esta guia explica como agregar nuevo contenido (posts de blog y proyectos) al portafolio en ambos idiomas.

---

## Folder Structure / Estructura de Carpetas

```
content/
├── es/                          # Spanish content
│   ├── blog/
│   │   ├── arquitectura/        # Architecture category
│   │   ├── fasthtml/            # FastHTML category
│   │   ├── machine-learning/    # ML category
│   │   └── python/              # Python category
│   └── projects/                # Project pages
└── en/                          # English content
    ├── blog/
    │   ├── arquitectura/
    │   ├── fasthtml/
    │   ├── machine-learning/
    │   └── python/
    └── projects/
```

---

## Adding a Blog Post / Agregar un Post de Blog

### 1. Create the Spanish version first / Crear primero la version en espanol

Create a new `.md` file in the appropriate category folder:

```bash
# Example: New post about Django
content/es/blog/python/mi-nuevo-post.md
```

### 2. Blog Post Frontmatter

Every blog post must have this YAML frontmatter at the top:

```yaml
---
title: Titulo del Post              # Required - Display title
slug: mi-nuevo-post                 # Required - URL slug (keep same in both languages)
date: 2024-12-31                    # Required - Publication date (YYYY-MM-DD)
tags:                               # Required - List of tags
  - Python
  - Django
  - Web Development
excerpt: Descripcion breve del post # Required - Summary shown in blog list
---
```

### 3. Blog Post Content

After the frontmatter, write your content in Markdown:

```markdown
# Main Title

Introduction paragraph...

## Section 1

Content with **bold** and *italic* text.

### Code Example

\`\`\`python
def hello():
    return "Hello World"
\`\`\`

## Conclusion

Final thoughts...
```

### 4. Create the English version / Crear la version en ingles

Copy the file to the same path under `en/`:

```bash
# Spanish version
content/es/blog/python/mi-nuevo-post.md

# English version (same slug!)
content/en/blog/python/mi-nuevo-post.md
```

**Important**: Keep the same `slug` in both versions so the language switcher works correctly.

---

## Adding a Project / Agregar un Proyecto

### 1. Project Frontmatter

```yaml
---
title: Project Name                      # Required
slug: project-slug                       # Required - URL slug (same in both languages)
technologies:                            # Required - Tech stack
  - Python
  - FastHTML
  - PostgreSQL
github: https://github.com/user/repo     # Optional - GitHub link
demo: https://demo-url.com               # Optional - Live demo URL (null if none)
featured: true                           # Required - Show in featured section
image: /static/images/project.jpg        # Optional - Project image
excerpt: Brief project description       # Required - Summary for cards
---
```

### 2. Project Content

Write detailed content about the project:

```markdown
# Project Name

Brief description of what the project does.

## Problem Solved

What problem does this project address?

## Technical Implementation

### Architecture

\`\`\`
Diagram or structure explanation
\`\`\`

### Key Features

- Feature 1
- Feature 2
- Feature 3

## Results

Metrics, outcomes, or achievements.

## Lessons Learned

What you learned from this project.
```

### 3. Add Project Image

Place the project image in:
```
static/images/project-name.jpg
```

Reference it in frontmatter as `/static/images/project-name.jpg`

---

## Creating a New Blog Category / Crear Nueva Categoria de Blog

1. Create the folder in both languages:
```bash
mkdir -p content/es/blog/nueva-categoria
mkdir -p content/en/blog/new-category
```

2. The category name comes from the folder name in URL paths.

---

## Translation Checklist / Lista de Verificacion de Traduccion

When creating content in both languages, ensure:

- [ ] Same `slug` in both versions
- [ ] Same `date` in both versions
- [ ] Translated `title` and `excerpt`
- [ ] Tags can be in English (they work as identifiers)
- [ ] All content text is translated
- [ ] Code comments can stay in English
- [ ] Technical terms can stay in English if commonly used

---

## UI Translations / Traducciones de UI

UI text translations are in the `locales/` folder:

```
locales/
├── es.yml    # Spanish translations
└── en.yml    # English translations
```

### Adding New UI Text

1. Add the key in both files:

```yaml
# locales/es.yml
section:
  new_text: "Texto nuevo"

# locales/en.yml
section:
  new_text: "New text"
```

2. Use in code with `t()` function:
```python
from services.i18n import t

# In component
P(t('section.new_text'))
```

---

## Quick Reference / Referencia Rapida

| Action | Spanish Path | English Path |
|--------|--------------|--------------|
| New blog post | `content/es/blog/{category}/{slug}.md` | `content/en/blog/{category}/{slug}.md` |
| New project | `content/es/projects/{slug}.md` | `content/en/projects/{slug}.md` |
| UI translation | `locales/es.yml` | `locales/en.yml` |

---

## Testing / Pruebas

After adding content:

1. Run the server: `python main.py`
2. Check Spanish: `http://localhost:5001/?lang=es`
3. Check English: `http://localhost:5001/?lang=en`
4. Verify the new content appears in both languages
5. Test the language switcher on the new content page

---

## Common Issues / Problemas Comunes

### Content not appearing / Contenido no aparece
- Check YAML frontmatter syntax (no tabs, proper indentation)
- Verify file has `.md` extension
- Check the slug is unique

### Language switcher doesn't work / El cambiador de idioma no funciona
- Ensure both versions have the **exact same slug**
- Check both files exist in their respective folders

### Images not loading / Imagenes no cargan
- Verify path starts with `/static/images/`
- Check file exists in `static/images/`
- Use lowercase filenames without spaces
