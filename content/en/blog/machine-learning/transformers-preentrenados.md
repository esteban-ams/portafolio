---
title: Pre-trained Transformers
slug: pre-trained-transformers
date: 2024-01-20
tags:
  - Python
  - Transformers
  - NLP
excerpt: Discover how to use pre-trained transformer models for NLP tasks.
---

# Pre-trained Transformer Models

Pre-trained transformer models have revolutionized the field of natural language processing (NLP). These models, trained on enormous amounts of text, can be adapted to multiple tasks with minimal effort.

## Why Use Pre-trained Transformers

- **Time and resource savings**: No need to train from scratch
- **Better performance**: Leverage knowledge from billions of parameters
- **Versatility**: One model, multiple tasks

## Installation

```bash
pip install transformers torch
```

## Basic Example: Sentiment Analysis

```python
from transformers import pipeline

# Load pre-trained pipeline
nlp = pipeline('sentiment-analysis')

# Analyze text
result = nlp("I love using pre-trained transformers!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

## Other Available Pipelines

```python
# Text generation
generator = pipeline('text-generation')
generator("The future of AI is")

# Question answering
qa = pipeline('question-answering')
qa(question="What is Python?", context="Python is a programming language...")

# Translation
translator = pipeline('translation_en_to_es')
translator("Hello, how are you?")
```

## Popular Models

| Model | Primary Use |
|-------|-------------|
| BERT | Classification, NER |
| GPT-2 | Text generation |
| T5 | Translation, summarization |
| RoBERTa | Sentiment analysis |

## Conclusion

Pre-trained transformers democratize access to high-quality NLP models. With just a few lines of code, you can solve complex language processing problems.
