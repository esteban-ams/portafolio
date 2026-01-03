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
excerpt: Chilean media monitoring system with async crawlers, Kafka pipeline for real-time processing, and semantic search with vector embeddings in pgvector.
---

# OpenMedia

Monitoring and analysis system for Chilean news media. Processes news in real-time, generates semantic embeddings, and enables intelligent content search.

## Motivation

Researchers, journalists, and analysts need to monitor multiple news outlets daily. The manual process is:
- Tedious: reviewing 20+ sites every day
- Incomplete: easy to miss relevant news
- Without context: difficult to connect related topics

## Architecture

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

## Components

### Async Crawlers

Specialized scrapers for each media outlet:

```python
class BaseCrawler:
    """Base for all media crawlers."""

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
        """Implemented by each specific media."""
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

### Kafka Pipeline

Real-time event processing:

```python
# Producer: Crawlers send raw articles
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


# Consumer: Workers process and enrich
async def consume_and_process():
    consumer = AIOKafkaConsumer(
        'raw-articles',
        bootstrap_servers='kafka:9092',
        group_id='article-processors'
    )

    async for msg in consumer:
        article = RawArticle.parse_raw(msg.value)

        # Extract full content
        full_content = await fetch_full_article(article.url)

        # Generate embedding
        embedding = generate_embedding(full_content.text)

        # Save in PostgreSQL + pgvector
        await save_article_with_embedding(
            article=full_content,
            embedding=embedding
        )
```

### Embeddings with Transformers

Using multilingual models for semantic representation:

```python
from sentence_transformers import SentenceTransformer

# Model optimized for Spanish
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def generate_embedding(text: str) -> List[float]:
    """Generates 384-dimension embedding."""
    # Truncate to 512 tokens max
    text = text[:2000]

    # Generate embedding
    embedding = model.encode(text, normalize_embeddings=True)

    return embedding.tolist()
```

### Semantic Search with pgvector

```sql
-- pgvector extension in PostgreSQL
CREATE EXTENSION vector;

-- Articles table with embedding
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    content TEXT,
    source VARCHAR(50),
    published_at TIMESTAMP,
    embedding vector(384)
);

-- Index for fast search
CREATE INDEX ON articles
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

```python
# Semantic search
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

## Search API

```python
@app.get("/search")
async def search(
    q: str,
    source: Optional[str] = None,
    date_from: Optional[date] = None,
    limit: int = 20
):
    # Semantic search
    results = await semantic_search(q, limit=limit * 2)

    # Additional filters
    if source:
        results = [r for r in results if r.source == source]

    if date_from:
        results = [r for r in results if r.published_at >= date_from]

    return results[:limit]


@app.get("/related/{article_id}")
async def get_related(article_id: int, limit: int = 5):
    """Find semantically similar articles."""
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

## Results

| Metric | Value |
|--------|-------|
| Media outlets monitored | 15+ |
| Articles processed/day | ~2,000 |
| Indexing latency | < 5 min |
| Search precision | ~85% |

## Use Cases

1. **Topic monitoring**: Alerts when news about specific topics appears
2. **Coverage analysis**: How different media cover the same event
3. **Research**: Search historical articles by semantic similarity
4. **Trend detection**: Identify emerging topics

## Key Technologies

- **aiohttp**: High-performance async crawling
- **Kafka**: Message queue for distributed processing
- **pgvector**: Vector search in PostgreSQL
- **Sentence Transformers**: Multilingual embeddings
- **Docker Compose**: Service orchestration
