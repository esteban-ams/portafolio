---
title: OpenMedia
slug: openmedia
technologies:
  - Python
  - Kafka
  - pgvector
  - Transformers
  - Docker
github: https://github.com/estebanmartinezsoto/openmedia
demo: null
featured: false
image: /static/images/openmedia.jpg
excerpt: Sistema de monitoreo de medios chilenos con crawlers asincronicos, pipeline Kafka para procesamiento en tiempo real, y busqueda semantica con embeddings vectoriales en pgvector.
---

# OpenMedia

Sistema de monitoreo y analisis de medios de comunicacion chilenos. Procesa noticias en tiempo real, genera embeddings semanticos, y permite busqueda inteligente de contenido.

## Motivacion

Investigadores, periodistas y analistas necesitan monitorear multiples medios de comunicacion diariamente. El proceso manual es:
- Tedioso: revisar 20+ sitios cada dia
- Incompleto: es facil perderse noticias relevantes
- Sin contexto: dificil conectar temas relacionados

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenMedia Pipeline                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐ │
│  │ Crawlers │───▶│  Kafka   │───▶│ Processor│───▶│  PostgreSQL  │ │
│  │ (async)  │    │  Topics  │    │ Workers  │    │  + pgvector  │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘ │
│       │                                                  │         │
│       ▼                                                  ▼         │
│  ┌──────────┐                                     ┌──────────────┐ │
│  │  Redis   │                                     │  Search API  │ │
│  │  Cache   │                                     │   (FastAPI)  │ │
│  └──────────┘                                     └──────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Componentes

### Crawlers Asincronicos

Scrapers especializados para cada medio:

```python
class BaseCrawler:
    """Base para todos los crawlers de medios."""

    async def fetch_articles(self) -> List[RawArticle]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page(session, url) for url in self.feed_urls]
            pages = await asyncio.gather(*tasks)

            articles = []
            for page in pages:
                articles.extend(self.parse_page(page))

            return articles

    async def fetch_page(self, session, url: str) -> str:
        async with session.get(url, headers=self.headers) as response:
            return await response.text()

    @abstractmethod
    def parse_page(self, html: str) -> List[RawArticle]:
        """Implementado por cada medio especifico."""
        pass


class EmolCrawler(BaseCrawler):
    feed_urls = [
        'https://www.emol.com/noticias/Nacional/',
        'https://www.emol.com/noticias/Economia/',
    ]

    def parse_page(self, html: str) -> List[RawArticle]:
        soup = BeautifulSoup(html, 'lxml')
        articles = []

        for card in soup.select('.col_center_noticia'):
            articles.append(RawArticle(
                url=card.select_one('a')['href'],
                title=card.select_one('h1').text.strip(),
                source='emol',
                scraped_at=datetime.now()
            ))

        return articles
```

### Pipeline Kafka

Procesamiento de eventos en tiempo real:

```python
# Producer: Crawlers envian articulos crudos
async def produce_articles(articles: List[RawArticle]):
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')
    await producer.start()

    for article in articles:
        await producer.send(
            'raw-articles',
            value=article.json().encode(),
            key=article.url.encode()
        )

    await producer.stop()


# Consumer: Workers procesan y enriquecen
async def consume_and_process():
    consumer = AIOKafkaConsumer(
        'raw-articles',
        bootstrap_servers='kafka:9092',
        group_id='article-processors'
    )

    async for msg in consumer:
        article = RawArticle.parse_raw(msg.value)

        # Extraer contenido completo
        full_content = await fetch_full_article(article.url)

        # Generar embedding
        embedding = generate_embedding(full_content.text)

        # Guardar en PostgreSQL + pgvector
        await save_article_with_embedding(
            article=full_content,
            embedding=embedding
        )
```

### Embeddings con Transformers

Uso de modelos multilingues para representacion semantica:

```python
from sentence_transformers import SentenceTransformer

# Modelo optimizado para espanol
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def generate_embedding(text: str) -> List[float]:
    """Genera embedding de 384 dimensiones."""
    # Truncar a 512 tokens max
    text = text[:2000]

    # Generar embedding
    embedding = model.encode(text, normalize_embeddings=True)

    return embedding.tolist()
```

### Busqueda Semantica con pgvector

```sql
-- Extension pgvector en PostgreSQL
CREATE EXTENSION vector;

-- Tabla de articulos con embedding
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    content TEXT,
    source VARCHAR(50),
    published_at TIMESTAMP,
    embedding vector(384)
);

-- Indice para busqueda rapida
CREATE INDEX ON articles
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

```python
# Busqueda semantica
async def semantic_search(query: str, limit: int = 10) -> List[Article]:
    query_embedding = generate_embedding(query)

    results = await db.fetch_all("""
        SELECT *, 1 - (embedding <=> :query_embedding) as similarity
        FROM articles
        ORDER BY embedding <=> :query_embedding
        LIMIT :limit
    """, {
        'query_embedding': str(query_embedding),
        'limit': limit
    })

    return [Article(**r) for r in results]
```

## API de Busqueda

```python
@app.get("/search")
async def search(
    q: str,
    source: Optional[str] = None,
    date_from: Optional[date] = None,
    limit: int = 20
):
    # Busqueda semantica
    results = await semantic_search(q, limit=limit * 2)

    # Filtros adicionales
    if source:
        results = [r for r in results if r.source == source]

    if date_from:
        results = [r for r in results if r.published_at >= date_from]

    return results[:limit]


@app.get("/related/{article_id}")
async def get_related(article_id: int, limit: int = 5):
    """Encuentra articulos semanticamente similares."""
    article = await get_article(article_id)

    return await db.fetch_all("""
        SELECT *, 1 - (embedding <=> :embedding) as similarity
        FROM articles
        WHERE id != :article_id
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """, {
        'embedding': str(article.embedding),
        'article_id': article_id,
        'limit': limit
    })
```

## Resultados

| Metrica | Valor |
|---------|-------|
| Medios monitoreados | 15+ |
| Articulos procesados/dia | ~2,000 |
| Latencia de indexacion | < 5 min |
| Precision de busqueda | ~85% |

## Casos de Uso

1. **Monitoreo de temas**: Alertas cuando aparecen noticias sobre temas especificos
2. **Analisis de cobertura**: Como diferentes medios cubren un mismo evento
3. **Investigacion**: Buscar articulos historicos por similitud semantica
4. **Deteccion de tendencias**: Identificar temas emergentes

## Tecnologias Clave

- **aiohttp**: Crawling asincrono de alto rendimiento
- **Kafka**: Cola de mensajes para procesamiento distribuido
- **pgvector**: Busqueda vectorial en PostgreSQL
- **Sentence Transformers**: Embeddings multilingues
- **Docker Compose**: Orquestacion de servicios
