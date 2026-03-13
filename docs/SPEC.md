# Fresh V2 - Agent Knowledge System Specification

## Overview

Fresh V2 is an **internal agent** that works on behalf of end agents (Claude Code, custom agents, etc.). It fetches documentation, analyzes it, and generates learning guides - all in service of making the end agent smarter and more effective.

```
End Agent: "I need to build something with Zod"
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                        Fresh Agent                           │
│  1. Analyze request                                          │
│  2. Check existing knowledge                                 │
│  3. Fetch fresh docs if needed                              │
│  4. Generate guide                                           │
│  5. Return Markdown output                                  │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼ (Markdown)
┌──────────────────────────────────────────────────────────────┐
│                    End Agent receives:                      │
│  # Zod v4 Migration Guide                                   │
│  ## What's new                                               │
│  - z.email() replaces z.string().email()                    │
│  ...                                                         │
└──────────────────────────────────────────────────────────────┘
```

## Core Problem

Current agents lack:
- **Continuity** - Each conversation starts from scratch
- **Updated knowledge** - They use outdated information
- **Synthesis** - They can't generate actionable learning guides
- **Memory** - They forget what they learned

Fresh V2 solves this by being an **always-available knowledge partner** for agents.

## Core Features

### 1. Knowledge Fetching

Fresh fetches the latest documentation from any source:
- Official documentation sites
- GitHub repositories
- APIs
- Package registries

**Example:**
```
fresh fetch zod
→ Fetches latest Zod docs, stores in knowledge base
```

### 2. Smart Detection

Fresh detects what's relevant to the user's needs:
- Which technologies are involved
- What versions are being used
- What has changed since last fetch

**Example:**
```
User: "help me with authentication in Next.js"
Fresh detects:
- Next.js version
- Auth libraries (NextAuth, Clerk, etc.)
- Recent changes in auth patterns
```

### 3. Guide Generation

Fresh generates actionable learning guides in Markdown:
- Summarized concepts
- Code examples
- Migration guides (v3 → v4)
- Best practices

**Output is always Markdown** - agents can read it directly.

### 4. Knowledge Base

All fetched docs and generated guides are stored:
- **SQLite** for indexing and fast queries
- **Markdown files** for human-readable output
- **Versioning** to track changes over time

## User Flow

### Explicit Learning

```
1. User → "fresh learn zod v4"
2. Fresh checks: "Do I already have Zod v4 guides?"
3. If yes → return existing guides
4. If no → fetch docs → analyze → generate → store → return
```

### Implicit Learning

```
1. User → "validate this form with zod"
2. Fresh analyzes → "user needs Zod"
3. Fresh checks → "do I know Zod?"
4. If no/freshness expired → auto-fetch and learn
5. Fresh provides relevant context + generates guide
6. User gets: context + guide reference
```

## Trigger Modes

### Manual Mode

User explicitly requests learning:
- `fresh learn <topic>`
- `fresh sync <url>`
- `fresh update zod`

### Automatic Mode

Fresh proactively learns:
- Detects unknown technology in request
- Fetches docs in background
- Generates guide
- Returns with response

### Hybrid Mode

Configuration-based:
- Always fetch critical tools (React, TypeScript, etc.)
- Auto-learn on first mention
- Manual for niche technologies

## Agent Behavior

### Decision Engine

When Fresh receives a request:

```
1. Parse intent (learn, fetch, search, generate)
2. Extract topics/technologies
3. Check knowledge base:
   - Do I have this topic?
   - Is it fresh? (configurable TTL)
4. If needed: fetch → analyze → generate
5. Return Markdown + metadata
```

### Analysis Capabilities

Fresh agent can:
- Compare versions (v3 vs v4)
- Extract code patterns
- Identify breaking changes
- Summarize complex APIs
- Generate code examples

## Storage Architecture

### SQLite Schema (conceptual)

```sql
-- Topics/Technologies
CREATE TABLE topics (
    id TEXT PRIMARY KEY,
    name TEXT,
    current_version TEXT,
    last_updated TIMESTAMP,
    metadata JSON
);

-- Fetched Documentation
CREATE TABLE docs (
    id TEXT PRIMARY KEY,
    topic_id TEXT,
    url TEXT,
    content TEXT,
    fetched_at TIMESTAMP,
    version TEXT
);

-- Generated Guides
CREATE TABLE guides (
    id TEXT PRIMARY KEY,
    topic_id TEXT,
    title TEXT,
    content TEXT,  -- Markdown
    generated_at TIMESTAMP,
    source_version TEXT
);

-- Search Index
CREATE VIRTUAL TABLE search USING fts5(
    topic, content, guide_title
);
```

### File Storage

```
~/.fresh/
├── knowledge/
│   ├── zod/
│   │   ├── docs/
│   │   │   ├── v4.0.0.md
│   │   │   └── v4.1.0.md
│   │   └── guides/
│   │       ├── v4-migration.md
│   │       └── basics.md
│   └── nextjs/
│       └── ...
└── index.db  # SQLite index
```

## Output Format

All outputs are **Markdown** for maximum compatibility:

```markdown
# Zod v4 Migration Guide

## Overview
Zod v4 introduces breaking changes from v3.

## Breaking Changes

### Email Validation
- **v3**: `z.string().email()`
- **v4**: `z.email()`

## New Features

### Improved Types
- `z.email()`
- `z.url()`
- `z.uuid()`

## Code Examples

```typescript
// v4
const schema = z.object({
  email: z.email(),
  url: z.url()
});
```

## Resources
- [Official Changelog](link)
- [Migration Guide](link)
```

## Invocation Modes

Fresh supports two invocation modes:

### Mode 1: Fresh Agent (via SDK)

End agent asks question → Fresh Agent processes → returns response

```
End Agent: "I need to validate a form with Zod"
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  Fresh Agent (Internal)                      │
│  1. Analyze: "user needs Zod validation"                   │
│  2. Check knowledge base                                    │
│  3. If stale: fetch fresh docs                             │
│  4. Generate guide/response                                 │
│  5. Return Markdown                                         │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
End Agent receives guide + code examples
```

This mode is **magical** - the agent does the heavy lifting.

### Mode 2: Fresh CLI (Direct)

End agent directly invokes CLI → returns raw response

```
End Agent: `fresh get https://zod.dev/api`
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                     Fresh CLI                                │
│  - Just fetch and convert to Markdown                       │
│  - No learning/generation                                   │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
End Agent receives raw Markdown docs
```

### Comparison

| Aspect | Agent Mode | CLI Mode |
|--------|------------|----------|
| Intelligence | High (analyzes, generates) | Low (just fetches) |
| Learning | Yes (generates guides) | No |
| Latency | Higher (LLM calls) | Lower (direct) |
| Use case | "Teach me X" | "Get me doc X" |
| Complexity | More setup | Simple |

---

## Integration Points

### CLI

```bash
# Learn a topic
fresh learn zod

# Fetch docs only
fresh fetch zod

# Search existing knowledge
fresh search "email validation"

# Generate guide
fresh guide create zod-v4 --from-fetched

# Check what we know
fresh knowledge list
```

### MCP Server (Future)

```json
{
  "tool": "fresh_learn",
  "arguments": {
    "topic": "zod",
    "version": "v4",
    "focus": "migration"
  }
}
```

### Python SDK (Future)

```python
from fresh import FreshAgent

agent = FreshAgent()
guide = agent.learn("zod", version="v4", focus="migration")
print(guide.markdown)
```

## Configuration

```json
{
  "learning": {
    "mode": "hybrid",
    "auto_fetch": ["react", "typescript", "python"],
    "ttl_hours": 24
  },
  "storage": {
    "path": "~/.fresh",
    "max_docs_mb": 1000
  },
  "agents": {
    "internal_model": "mini-max",
    "temperature": 0.7
  }
}
```

## Roadmap

### Phase 1: Core (Current)
- [x] CLI commands (get, list, search, sync)
- [x] Guide management
- [ ] SQLite storage layer
- [ ] Knowledge base indexing

### Phase 2: Agent Features
- [ ] Internal LLM for analysis
- [ ] Auto-detection of topics
- [ ] Guide generation from docs
- [ ] Version comparison

### Phase 3: Integration
- [ ] MCP server
- [ ] Python SDK
- [ ] Plugin system

### Phase 4: Intelligence
- [ ] Learning from agent feedback
- [ ] Proactive knowledge updates
- [ ] Cross-topic synthesis
