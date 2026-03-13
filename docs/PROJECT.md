# Fresh - Agent Knowledge System

> A CLI tool to build and manage knowledge for coding. Used by humans and AI agents.

## What It Does

Two things:

1. **Sync docs** - Fetch documentation locally for offline use
2. **Learn** - Build structured knowledge through iterative learning

## Quick Start

```bash
# Get docs locally
fresh sync zod
fresh sync react

# Learn something new
fresh learn init probability-theory
fresh learn explore probability
fresh learn add probability-theory fundamentals --priority high
fresh learn next
```

## Structure

```
.fresh/
├── knowledge/           # Synced documentation
│   ├── zod/
│   └── react/
└── learning/           # Learning projects
    └── probability-theory/
```

## Commands

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch doc locally |
| `fresh search <query>` | Search docs |
| `fresh learn init <topic>` | Start learning |
| `fresh learn explore <topic>` | Discover concepts |
| `fresh learn add <path>` | Add content |
| `fresh learn queue` | See queue |
| `fresh learn next` | Get next concept |
| `fresh learn start <concept>` | Start concept |
| `fresh learn done <concept>` | Mark complete |
| `fresh learn link <a> <b>` | Link concepts |

## For Humans & Agents

Fresh is a CLI. Both humans and AI agents use the same commands.

## License

MIT
