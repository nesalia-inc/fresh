# Fresh V2 - Agent Knowledge System Specification

## Overview

Fresh V2 is a **project-local documentation and knowledge management system** for AI agents. Each project has its own `.fresh/` directory containing:

- **Synced documentation** - Fetched docs for offline use
- **Project guides** - Agent-created learning guides
- **Search index** - Local search capability

```
my-project/
├── src/
├── .fresh/                    # Fresh data (project-local)
│   ├── knowledge/             # Synced docs (zod, react, etc.)
│   │   ├── zod/
│   │   │   ├── docs/
│   │   │   │   ├── getting-started.md
│   │   │   │   └── api/
│   │   │   └── metadata.json
│   │   └── react/
│   │       └── ...
│   ├── guides/               # Agent-created guides
│   │   ├── optimistic-state.md
│   │   └── zod-validation.md
│   ├── index.db              # Search index
│   └── config.json           # Project config
└── ...
```

## Core Philosophy

1. **Project-local** - Each project has its own `.fresh/` directory
2. **Scraping first** - Get docs locally, keep them available
3. **Agent-authored guides** - Agents create and enrich their own guides
4. **CLI primary** - Agent only when necessary

---

## Core Features

### 1. Scraping Engine

Fetch documentation sites locally:

```bash
# Fetch docs for a topic
fresh sync zod           # → .fresh/knowledge/zod/
fresh sync react        # → .fresh/knowledge/react/

# Fetch specific version
fresh sync zod --version v4
```

**Output:** Markdown files in `.fresh/knowledge/{topic}/`

### 2. Local Search

Search across all synced documentation:

```bash
# Search all topics
fresh search "email validation"

# Search specific topic
fresh search "email validation" zod
```

### 3. Guide System

Agents create and enrich their own guides:

```bash
# Create empty guide
fresh guide create optimistic-state

# Add content to guide
fresh guide add optimistic-state --content "# Optimistic Updates\n\n..."

# Add from search results
fresh guide add optimistic-state --from-search "optimistic update"

# Show guide
fresh guide show optimistic-state

# List all guides
fresh guide list
```

**Guides are Markdown files** in `.fresh/guides/`

### 4. Knowledge Status

```bash
# List all synced docs
fresh knowledge list

# Check specific topic
fresh knowledge status zod

# Refresh topic docs
fresh knowledge refresh zod
```

---

## User Flows

### Flow 1: First-time Project Setup

```bash
# In project directory
cd my-project

# Fetch docs you need
fresh sync zod
fresh sync react
fresh sync typescript

# Check what's available
fresh knowledge list
```

### Flow 2: Creating a Guide

```bash
# Agent decides to create a guide for learning
fresh guide create optimistic-state-management

# Agent adds content (manually or from search)
fresh guide add optimistic-state-management \
  --from-search "optimistic update react"

fresh guide add optimistic-state-management \
  --from-search "useMutation"

# Agent enriches with own notes
fresh guide add optimistic-state-management \
  --content "# Best Practices\n\n- Always rollback on error\n..."

# Check the guide
fresh guide show optimistic-state-management
```

### Flow 3: Using a Guide

```bash
# Agent needs context
fresh guide list                      # See available guides
fresh guide show optimistic-state     # Read the guide
```

### Flow 4: Searching

```bash
# Find info in synced docs
fresh search "zustand store"

# Search specific topic
fresh search "zustand store" zustand
```

---

## Guide Structure

A guide is a Markdown file in `.fresh/guides/`:

```markdown
# Optimistic State Management

> Created: 2026-03-13
> Topics: react, react-query, zustand

## Overview

Techniques for implementing optimistic updates...

## With React Query

```typescript
useMutation({
  onMutate: async (newTodo) => {
    queryClient.cancelQueries({ queryKey: ['todos'] })
    const previousTodos = queryClient.getQueryData(['todos'])
    queryClient.setQueryData(['todos'], old => [...old, newTodo])
    return { previousTodos }
  }
})
```

## Best Practices

- Always provide rollback
- Handle errors gracefully

## Notes

> My notes: This is especially useful for user interactions that feel slow...
```

---

## Project Structure

When running Fresh in a project:

```
project/
├── .fresh/
│   ├── knowledge/              # Synced documentation
│   │   ├── zod/
│   │   │   ├── docs/
│   │   │   │   ├── getting-started.md
│   │   │   │   ├── api/
│   │   │   │   │   ├── schema.md
│   │   │   │   │   └── validators.md
│   │   │   │   └── ...
│   │   │   └── metadata.json
│   │   ├── react/
│   │   │   └── ...
│   │   └── typescript/
│   │       └── ...
│   ├── guides/                 # Agent-created guides
│   │   ├── optimistic-state.md
│   │   ├── forms-with-zod.md
│   │   └── react-hooks.md
│   ├── index.db              # SQLite search index
│   └── config.json           # Project config
└── ...
```

### Metadata

Each topic has metadata:

```json
// .fresh/knowledge/zod/metadata.json
{
  "topic": "zod",
  "version": "4.0.0",
  "synced_at": "2026-03-13T10:00:00Z",
  "source_url": "https://zod.dev",
  "pages": 45
}
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch doc site locally |
| `fresh sync <topic> --version v4` | Fetch specific version |
| `fresh search <query>` | Search all topics |
| `fresh search <query> <topic>` | Search specific topic |
| `fresh guide create <name>` | Create new guide |
| `fresh guide add <name> --content "..."` | Add content to guide |
| `fresh guide add <name> --from-search "..."` | Add from search results |
| `fresh guide show <name>` | Show guide content |
| `fresh guide list` | List all guides |
| `fresh guide delete <name>` | Delete a guide |
| `fresh knowledge list` | List synced docs |
| `fresh knowledge status <topic>` | Show topic status |
| `fresh knowledge refresh <topic>` | Re-sync topic |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                               │
│   sync │ search │ guide │ knowledge                        │
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
│                   Storage (.fresh/)                         │
│          SQLite (index) + Markdown (docs & guides)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Roadmap

### Phase 1 (Core)
- [x] CLI commands
- [x] Guide creation
- [ ] Project-local `.fresh/` directory
- [ ] SQLite search index

### Phase 2
- [ ] Better guide enrichment
- [ ] Search improvements

### Phase 3 (Optional)
- [ ] Agent for complex synthesis
- [ ] MCP server
- [ ] Python SDK
