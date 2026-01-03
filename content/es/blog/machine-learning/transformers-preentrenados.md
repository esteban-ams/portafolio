---
title: Transformers Preentrenados
slug: pre-trained-transformers
date: 2024-01-20
tags:
  - Python
  - Transformers
  - NLP
excerpt: Descubre como usar modelos de transformers preentrenados para tareas de NLP.
---

# Modelos Transformadores Preentrenados

Los modelos transformadores preentrenados han revolucionado el campo del procesamiento del lenguaje natural (NLP). Estos modelos, entrenados en enormes cantidades de texto, pueden ser adaptados para multiples tareas con minimo esfuerzo.

## Por que usar Transformers Preentrenados

- **Ahorro de tiempo y recursos**: No necesitas entrenar desde cero
- **Mejor rendimiento**: Aprovechas el conocimiento de billones de parametros
- **Versatilidad**: Un modelo, multiples tareas

## Instalacion

```bash
pip install transformers torch
```

## Ejemplo basico: Analisis de sentimiento

```python
from transformers import pipeline

# Cargar pipeline preentrenado
nlp = pipeline('sentiment-analysis')

# Analizar texto
result = nlp("I love using pre-trained transformers!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

## Otros pipelines disponibles

```python
# Generacion de texto
generator = pipeline('text-generation')
generator("El futuro de la IA es")

# Preguntas y respuestas
qa = pipeline('question-answering')
qa(question="Que es Python?", context="Python es un lenguaje de programacion...")

# Traduccion
translator = pipeline('translation_en_to_es')
translator("Hello, how are you?")
```

## Modelos populares

| Modelo | Uso principal |
|--------|--------------|
| BERT | Clasificacion, NER |
| GPT-2 | Generacion de texto |
| T5 | Traduccion, resumen |
| RoBERTa | Analisis de sentimiento |

## Conclusion

Los transformers preentrenados democratizan el acceso a modelos de NLP de alta calidad. Con pocas lineas de codigo puedes resolver problemas complejos de procesamiento de lenguaje.
