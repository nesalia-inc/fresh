# Fresh - Agent Knowledge System

> A documentation scraping and knowledge management system for AI agents.

## Purpose

Fresh is a tool that enables AI agents to:
1. **Fetch documentation locally** - Get entire doc sites in Markdown format
2. **Keep docs available** - Offline access to any documentation
3. **Create guides** - Synthesize knowledge into actionable guides
4. **Search efficiently** - Find information across all local docs

## Core Philosophy

1. **Scraping first** - The most important feature is getting docs locally
2. **CLI as primary** - Fast, reliable, deterministic
3. **Agent only when needed** - For complex synthesis only

## The Problem

AI agents need context to produce quality code. But:
- Docs are online, not always available
- Each conversation starts from scratch
- Can't create reusable knowledge
- Hard to find relevant information

## The Solution

```
┌─────────────────────────────────────────────────────────────────┐
│                     Fresh Core (CLI)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Scraping     │  │   Local Docs   │  │    Search      │ │
│  │   (sync)       │  │   Storage      │  │    (search)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Guide Layer (CLI + Optional Agent)             │
│  ┌─────────────────┐  ┌─────────────────┐                     │
│  │   CLI Guide    │  │   Agent (opt)   │                     │
│  │   Creation     │  │   Synthesis    │                     │
│  └─────────────────┘  └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## User Flow

### Step 1: Fetch Docs (CLI)

```bash
fresh sync zod        # Get all Zod docs locally
fresh sync react      # Get React docs
fresh sync python     # Get Python docs
```

### Step 2: Search (CLI)

```bash
fresh search "email validation" zod
# → Finds relevant sections in local Zod docs
```

### Step 3: Create Guide (CLI)

```bash
fresh guide create zod-validation \
  --from-search "email validation" \
  --from-search "string validation"
```

### Step 4: Learn (Agent - Optional)

For complex synthesis:
```bash
fresh learn "optimistic state" \
  --sources react tanstack-query zustand \
  --agent
```

## Commands

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch entire doc site locally |
| `fresh get <url>` | Fetch single page |
| `fresh list <url>` | List available pages |
| `fresh search <query>` | Search local docs |
| `fresh guide create <name>` | Create a guide |
| `fresh guide list` | List all guides |
| `fresh knowledge list` | Show local docs |

## Documentation

- **[SPEC.md](SPEC.md)** - Product specification and features
- **[AGENT.md](AGENT.md)** - Optional agent for complex cases
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture

## Roadmap

### Phase 1 (Core)
- [x] CLI commands (get, list, search, sync)
- [x] Guide management
- [ ] Improved scraping engine
- [ ] SQLite storage

### Phase 2
- [ ] Better guide creation from search
- [ ] Search improvements

### Phase 3 (Optional)
- [ ] Agent for complex synthesis
- [ ] MCP server
- [ ] Python SDK

## License

MIT
