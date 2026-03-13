# Fresh - Agent Knowledge System

> A project-local documentation and knowledge management system for AI agents.

## Purpose

Fresh enables AI agents to:
1. **Fetch documentation locally** - Get doc sites in Markdown, available offline
2. **Create project guides** - Agents create and enrich their own learning guides
3. **Search efficiently** - Find info across all synced docs

## Core Concept

**Project-local knowledge:** Each project has its own `.fresh/` directory:

```
my-project/
├── src/
├── .fresh/                    # Fresh data (project-local)
│   ├── knowledge/             # Synced docs (zod, react, etc.)
│   │   ├── zod/
│   │   └── react/
│   ├── guides/               # Agent-created guides
│   │   ├── optimistic-state.md
│   │   └── forms-with-zod.md
│   └── index.db              # Search index
└── ...
```

## Core Philosophy

1. **Project-local** - Each project manages its own docs and guides
2. **Scraping first** - Get docs locally, keep them available
3. **Agent-authored** - Agents create and enrich their own guides
4. **CLI primary** - Agent only when necessary

## User Flow

### Step 1: Fetch Docs (CLI)

```bash
fresh sync zod        # → .fresh/knowledge/zod/
fresh sync react      # → .fresh/knowledge/react/
```

### Step 2: Search (CLI)

```bash
fresh search "email validation"
# → Searches in .fresh/knowledge/
```

### Step 3: Create/Enrich Guides (CLI)

```bash
# Create guide
fresh guide create optimistic-state

# Agent adds content
fresh guide add optimistic-state --content "# Optimistic Updates\n\n..."
fresh guide add optimistic-state --from-search "optimistic update react"

# Read guide
fresh guide show optimistic-state
fresh guide list
```

## Commands

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch doc site locally |
| `fresh search <query>` | Search local docs |
| `fresh guide create <name>` | Create a guide |
| `fresh guide add <name>` | Add content to guide |
| `fresh guide show <name>` | Show guide content |
| `fresh guide list` | List all guides |
| `fresh knowledge list` | Show synced docs |

## Documentation

- **[SPEC.md](SPEC.md)** - Full specification
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture

## License

MIT
