# Fresh V2 - Agent Knowledge System Specification

## Overview

Fresh V2 is a **documentation scraping and knowledge management system** designed for AI agents. The core value is simple: **fetch documentation locally, keep it available, and enable agents to create guides from it.**

```
┌─────────────────────────────────────────────────────────────────┐
│                     Fresh Core                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   Scraping     │  │   Local Docs   │  │    Search      │   │
│  │   Engine      │  │   Storage      │  │    Engine      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Guide Creation Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   CLI Tools    │  │   Agent (opt)  │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Core Philosophy

1. **Scraping first** - Get docs local, keep them available offline
2. **CLI as primary** - Agent only when necessary
3. **Guides are key** - Agents create and use guides for learning

---

## Core Features

### 1. Scraping Engine (Core)

The most important feature: **get entire documentation sites locally in correct Markdown format.**

```
fresh sync zod
→ Downloads all Zod docs to ~/.fresh/knowledge/zod/
→ Converts HTML to clean Markdown
→ Preserves structure (navigation, code blocks, etc.)
→ Available offline forever
```

**Requirements:**
- Fetch entire doc sites (not just one page)
- Convert HTML to readable Markdown
- Preserve code blocks, syntax highlighting references
- Keep site structure (navigation hierarchy)
- Handle multiple docs simultaneously
- Store locally, stay available

### 2. Local Documentation Storage

All fetched docs are stored locally:

```
~/.fresh/
├── knowledge/
│   ├── zod/
│   │   ├── docs/
│   │   │   ├── getting-started.md
│   │   │   ├── api/
│   │   │   │   ├── schema.md
│   │   │   │   └── validators.md
│   │   │   └── ...
│   │   └── metadata.json
│   ├── react/
│   │   └── ...
│   └── typescript/
│       └── ...
└── index.db  # Search index
```

### 3. Search Engine

Search across all local documentation:

```
fresh search "email validation" zod
→ Searches in local Zod docs
→ Returns relevant sections with context

fresh search "state management"
→ Searches across ALL local docs
→ Returns results from React, Vue, TanStack Query, etc.
```

### 4. Guide Creation

Agents create guides from local docs:

```
# Create guide from search results
fresh guide create optimistic-state-management \
  --topic react \
  --from-search "optimistic update" \
  --from-search "useMutation"

# Create guide manually
fresh guide create my-guide --content "# My Guide\n\nContent..."
```

**Guide structure:**
```markdown
# Optimistic State Management

## Overview
Techniques for implementing optimistic updates in React...

## With React Query
```typescript
useMutation({
  onMutate: async (newTodo) => {
    // Cancel outgoing refetches
    queryClient.cancelQueries({ queryKey: ['todos'] })
    // Snapshot previous value
    const previousTodos = queryClient.getQueryData(['todos'])
    // Optimistically update
    queryClient.setQueryData(['todos'], old => [...old, newTodo])
    return { previousTodos }
  }
})
```

## With Zustand
...

## Best Practices
- Always provide rollback
- Handle errors gracefully
```

---

## Invocation Modes

### Mode 1: CLI (Primary)

Everything via CLI commands - fast, simple, reliable.

```bash
# Scraping
fresh sync zod                    # Fetch all Zod docs
fresh sync react --depth 5        # Fetch React docs, depth 5
fresh sync                       # Sync all known docs

# Searching
fresh search "email validation" zod    # Search specific topic
fresh search "state management"         # Search all topics

# Guide management
fresh guide create my-guide --content "..."
fresh guide list
fresh guide show my-guide

# Knowledge status
fresh knowledge list              # Show all local docs
fresh knowledge status zod        # Show Zod doc status
fresh knowledge refresh zod       # Re-fetch Zod docs
```

**When to use CLI:**
- Fetching docs (scraping)
- Searching docs
- Basic guide creation
- Status checks
- Everything that's well-defined

### Mode 2: Agent (When Necessary)

Agent only for complex synthesis that CLI can't handle:

```python
from fresh import FreshAgent

agent = FreshAgent()

# Complex guide that needs synthesis across multiple sources
guide = agent.learn(
    topic="optimistic-state-management",
    sources=["react", "tanstack-query", "zustand"],
    focus="best-practices"
)
```

**When to use Agent:**
- Synthesizing guides from multiple topics
- Complex comparisons (v3 vs v4 migration)
- Generating guide structure from scratch
- Advanced analysis

**Rule:** If CLI can do it, CLI does it. Agent is opt-in for complexity.

---

## User Flows

### Flow 1: First-time Setup

```bash
# 1. Fetch docs you care about
fresh sync zod
fresh sync react
fresh sync typescript
fresh sync python

# 2. Check what's available
fresh knowledge list
```

### Flow 2: Daily Usage

```bash
# 1. Search for what you need
fresh search "email validation" zod

# 2. Create a guide from results
fresh guide create zod-validation \
  --from-search "email validation" \
  --from-search "string validation"

# 3. Use guide in your work
fresh guide show zod-validation
```

### Flow 3: Complex Learning (Agent)

```bash
# When you need advanced synthesis
fresh learn "optimistic updates" \
  --sources react tanstack-query \
  --agent  # Triggers agent for complex synthesis
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                               │
│   get │ list │ search │ sync │ guide │ alias              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scraping   │  │   Search     │  │    Guide    │     │
│  │   Service    │  │   Service    │  │   Service   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                             │
│          SQLite (index) + Markdown (docs)                   │
└─────────────────────────────────────────────────────────────┘
```

### Scraping Service

```python
class ScrapingService:
    """Fetches and converts documentation."""

    async def sync(url: str, options: SyncOptions) -> SyncResult:
        """Fetch entire doc site."""

    async def fetch_page(url: str) -> str:
        """Fetch single page as Markdown."""

    async def discover(url: str) -> list[str]:
        """Discover available pages."""

    async def convert(html: str, options: ConvertOptions) -> str:
        """Convert HTML to Markdown."""
```

### Search Service

```python
class SearchService:
    """Searches local documentation."""

    async def search(query: str, topic: str | None) -> list[SearchResult]:
        """Search docs."""

    async def index(topic_id: str) -> None:
        """Index topic for search."""
```

### Guide Service

```python
class GuideService:
    """Manages guide lifecycle."""

    async def create(title: str, content: str) -> Guide:
        """Create guide."""

    async def create_from_search(
        title: str,
        queries: list[str],
        topic: str | None
    ) -> Guide:
        """Create guide from search results."""

    async def get(guide_id: str) -> Guide:
        """Get guide."""

    async def list() -> list[Guide]:
        """List all guides."""
```

---

## Scraping Requirements

### Must Have

1. **Full site scraping** - Not just one page, entire docs
2. **Markdown conversion** - Clean, readable MD output
3. **Code preservation** - Keep code blocks intact
4. **Structure preservation** - Keep navigation/hierarchy
5. **Offline availability** - Docs stay local forever
6. **Multiple sources** - Handle any documentation site
7. **Incremental updates** - Only fetch what changed

### Quality Criteria

- [ ] All pages fetched
- [ ] Images handled (alt text or skipped)
- [ ] Code blocks preserved
- [ ] Links converted (relative → file, absolute → external)
- [ ] Navigation structure kept
- [ ] Searchable (indexed)

---

## Roadmap

### Phase 1: Scraping Core
- [ ] Full site scraping
- [ ] HTML → Markdown conversion
- [ ] Local storage
- [ ] Search indexing

### Phase 2: Guide System
- [ ] Guide CRUD
- [ ] Create from search
- [ ] Guide storage

### Phase 3: Agent (Optional)
- [ ] Agent for complex synthesis
- [ ] MCP server
- [ ] Python SDK

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch entire doc site locally |
| `fresh get <url>` | Fetch single page |
| `fresh list <url>` | List available pages |
| `fresh search <query>` | Search local docs |
| `fresh search <query> <topic>` | Search specific topic |
| `fresh guide create <name>` | Create new guide |
| `fresh guide list` | List all guides |
| `fresh guide show <name>` | Show guide content |
| `fresh knowledge list` | List local docs |
| `fresh knowledge refresh <topic>` | Re-fetch topic docs |
