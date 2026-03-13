# Fresh V2 Architecture

## Stack

- **CLI**: TypeScript (with tsup / oclif)
- **Web**: Next.js 16 (App Router)
- **Database**: PostgreSQL + Drizzle ORM
- **Language**: TypeScript everywhere

## Monorepo Structure

```
fresh/
├── apps/
│   ├── web/              # Next.js web app (registry, auth UI)
│   ├── api/              # Next.js API routes
│   └── cli/              # TypeScript CLI
│
├── packages/
│   ├── db/               # Drizzle ORM + migrations
│   ├── shared/           # Shared types, utils
│   ├── config/           # Configuration
│   └── fresh/            # Core library (shared by CLI & API)
│
└── turbo.json            # Turborepo config
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI (TypeScript)                        │
│   fresh sync | fresh learn | fresh registry                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Next.js API Server                         │
│   Auth | Registry | Sync                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL + Drizzle                          │
│   Users | Guides | Organizations | Registry                │
└─────────────────────────────────────────────────────────────┘
```
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Fresh Agent (Brain)                      │
│   Intent Parser │ Knowledge Engine │ Synthesis Engine      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Services                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  Fetch  │ │  Index  │ │ Search  │ │  Guide  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                            │
│          PostgreSQL + Drizzle (Index) + Markdown (Content)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Sources                                 │
│     Web (HTTP) │ Local Files │ Generated │ Plugins         │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Integration Layer

- **CLI**: User-facing command interface
- **MCP Server**: Model Context Protocol for agent integration
- **Python SDK**: Library import for programmatic access
- **Direct API**: HTTP API for custom integrations

### Fresh Agent (Brain)

The intelligent layer that orchestrates everything:
- Parses user intent
- Manages knowledge lifecycle
- Synthesizes outputs

### Core Services

| Service | Responsibility |
|---------|----------------|
| Fetch | Retrieve documentation from sources |
| Index | Build and maintain search index |
| Search | Query knowledge base |
| Guide | Generate and manage guides |

### Storage Layer

- **PostgreSQL**: Fast indexing, queries, metadata
- **Markdown**: Human-readable content, agent-friendly

### Sources

- **Web**: HTTP requests to documentation sites
- **Local**: Filesystem access
- **Generated**: Content created by Fresh
- **Plugins**: Extensible source system

## Storage Design

### PostgreSQL Schema

```sql
-- Core topics/technologies
CREATE TABLE topics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    current_version TEXT,
    description TEXT,
    homepage_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fetched documentation
CREATE TABLE docs (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    version TEXT,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    content_hash TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Generated guides
CREATE TABLE guides (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    version TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,  -- Markdown
    focus TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_doc_ids TEXT,  -- JSON array of doc IDs
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- User-created content
CREATE TABLE user_guides (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aliases for quick access
CREATE TABLE aliases (
    id TEXT PRIMARY KEY,
    alias TEXT UNIQUE NOT NULL,
    topic_id TEXT,
    url TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Search index
CREATE VIRTUAL TABLE search_idx USING fts5(
    topic_name,
    doc_title,
    doc_content,
    guide_title,
    guide_content,
    content='',
    content_rowid='rowid'
);

-- Triggers for search index
CREATE TRIGGER docs_ai AFTER INSERT ON docs BEGIN
    INSERT INTO search_idx(topic_name, doc_title, doc_content)
    SELECT t.name, new.title, new.content
    FROM topics t WHERE t.id = new.topic_id;
END;

CREATE TRIGGER guides_ai AFTER INSERT ON guides BEGIN
    INSERT INTO search_idx(topic_name, guide_title, guide_content)
    SELECT t.name, new.title, new.content
    FROM topics t WHERE t.id = new.topic_id;
END;

-- Indexes for performance
CREATE INDEX idx_docs_topic ON docs(topic_id);
CREATE INDEX idx_docs_version ON docs(topic_id, version);
CREATE INDEX idx_guides_topic ON guides(topic_id);
CREATE INDEX idx_guides_version ON guides(topic_id, version);
CREATE INDEX idx_user_guides_tags ON user_guides(tags);
```

### File Storage Structure

```
~/.fresh/
├── knowledge/              # Fetched docs and generated guides
│   ├── {topic-slug}/
│   │   ├── metadata.json   # Topic metadata
│   │   ├── docs/
│   │   │   ├── v4.0.0/
│   │   │   │   ├── index.md
│   │   │   │   └── {page-slug}.md
│   │   │   └── v3.x/
│   │   └── guides/
│   │       ├── v4-migration.md
│   │       └── basics.md
│   └── ...
├── user/                   # User-created content
│   └── guides/
│       └── {guide-slug}.md
├── cache/                  # Temporary cache
├── index.db               # PostgreSQL (hosted)
└── config.json            # User configuration
```

### Metadata JSON Structure

```json
{
  "id": "zod-v4",
  "name": "Zod",
  "slug": "zod",
  "current_version": "4.0.0",
  "homepage_url": "https://zod.dev",
  "description": "TypeScript-first schema validation",
  "topics": ["validation", "typescript", "schema"],
  "fetched_at": "2026-03-13T10:00:00Z",
  "versions": ["4.0.0", "3.x"],
  "last_guide": {
    "id": "zod-v4-migration",
    "generated_at": "2026-03-13T10:30:00Z"
  }
}
```

## Service Interfaces

### Fetch Service

```python
class FetchService:
    """Fetches documentation from various sources."""

    async def fetch(url: str, options: FetchOptions) -> FetchResult:
        """Fetch a single URL."""

    async def discover(url: str, options: DiscoverOptions) -> list[str]:
        """Discover available pages."""

    async def sync(url: str, options: SyncOptions) -> SyncResult:
        """Sync entire documentation site."""
```

### Index Service

```python
class IndexService:
    """Manages search index."""

    async def index(doc: Document) -> None:
        """Add document to index."""

    async def search(query: str, options: SearchOptions) -> list[SearchResult]:
        """Search the index."""

    async def reindex(topic_id: str) -> None:
        """Rebuild index for a topic."""
```

### Guide Service

```python
class GuideService:
    """Manages guide lifecycle."""

    async def generate(topic: str, version: str, focus: str) -> Guide:
        """Generate a new guide."""

    async def get(topic: str, guide_id: str) -> Guide:
        """Get existing guide."""

    async def list(topic: str) -> list[GuideSummary]:
        """List guides for a topic."""

    async def create(title: str, content: str, tags: list[str]) -> UserGuide:
        """Create a user guide."""

    async def search(query: str) -> list[GuideSummary]:
        """Search guides."""
```

### Knowledge Service

```python
class KnowledgeService:
    """Manages overall knowledge base."""

    async def know(topic: str) -> KnowledgeStatus:
        """Check if we know about a topic."""

    async def learn(topic: str, version: str, focus: str) -> LearnResult:
        """Main learning entry point."""

    async def refresh(topic: str) -> RefreshResult:
        """Refresh knowledge for a topic."""

    async def compare(topic: str, v1: str, v2: str) -> ComparisonResult:
        """Compare two versions."""
```

## Design Patterns

### Result Monad

All service methods return a `Result` type:

```python
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data)

    @classmethod
    def err(cls, error: str) -> "Result[T]":
        return cls(success=False, error=error)
```

### Entity-Oriented Design

Classes represent **what they are**, not what they do:

```python
# Good
class Guide:
    """A learning guide."""
    pass

class Document:
    """A fetched document."""
    pass

# Avoid
class GuideGenerator:
    """Generates guides."""

class DocumentFetcher:
    """Fetches documents."""
```

### Dependency Injection

Services are injected, not instantiated:

```python
class FreshAgent:
    def __init__(
        self,
        fetch: FetchService,
        index: IndexService,
        guide: GuideService,
        knowledge: KnowledgeService,
    ):
        self._fetch = fetch
        self._index = index
        self._guide = guide
        self._knowledge = knowledge
```

## Configuration

```python
from dataclasses import dataclass

@dataclass
class FreshConfig:
    """Fresh configuration."""

    # Storage
    storage_path: str = "~/.fresh"
    max_cache_mb: int = 1000

    # Learning behavior
    learning_mode: str = "hybrid"  # manual, auto, hybrid
    default_ttl_hours: int = 24
    auto_fetch_topics: list[str] = None

    # Agent
    internal_model: str = "mini-max"
    temperature: float = 0.7

    # Sources
    user_agent: str = "Fresh/2.0"
    timeout_seconds: int = 30
    max_retries: int = 3

    # MCP (if enabled)
    mcp_enabled: bool = False
    mcp_port: int = 8080
```

## CLI Commands Structure

```
fresh
├── get         # Fetch a doc page
├── list        # List available docs
├── search      # Search knowledge base
├── fetch       # Fetch docs for a topic
├── learn       # Fetch + generate guide
├── sync        # Sync entire docs site
├── guide       # Manage guides
│   ├── create
│   ├── list
│   ├── show
│   ├── edit
│   └── delete
├── alias       # Manage aliases
│   ├── add
│   ├── list
│   └── remove
└── knowledge   # Manage knowledge base
    ├── list
    ├── status
    └── refresh
```
