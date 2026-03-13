# Fresh - Agent Knowledge System

> A project-local knowledge system for AI agents with two modes: Run (daily usage) and Learn (building knowledge).

## The Two Modes

Fresh has **two distinct purposes**:

### Run Mode - Daily Usage

Agent **already has knowledge** and needs to retrieve it quickly.

```bash
# Search
fresh search "email validation"

# View guides
fresh guide show optimistic-state
fresh guide list

# Quick reference
fresh knowledge list
```

### Learn Mode - Building Knowledge

Agent **builds its knowledge** through iterative learning.

```bash
# Start learning
fresh learn init probability-theory
fresh learn explore probability

# Build structure
fresh learn chapter probability-theory 01-fundamentals

# Add content iteratively
fresh learn add probability-theory/01/sample-space --content "..."
fresh learn link probability-theory/01/sample-space -> probability-theory/02/conditional
```

## Project Structure

```
.fresh/
├── knowledge/                 # Run: Synced technical docs
│   ├── zod/
│   └── react/
├── guides/                   # Run: Quick reference guides
│   └── optimistic-state.md
└── learning/                 # Learn: Structured learning projects
    ├── probability-theory/
    │   ├── 01-fundamentals/
    │   └── 02-conditional/
    └── linear-algebra/
```

## Core Philosophy

1. **Project-local** - Each project manages its own knowledge
2. **Two modes** - Run (retrieve) vs Learn (create)
3. **Scraping first** - Get docs locally
4. **Iterative learning** - Discover, add, link, repeat

## Commands

### Run Mode

| Command | Description |
|---------|-------------|
| `fresh sync <topic>` | Fetch doc site locally |
| `fresh search <query>` | Search local docs |
| `fresh guide create <name>` | Create a guide |
| `fresh guide show <name>` | Show guide |
| `fresh guide list` | List guides |
| `fresh knowledge list` | Show synced docs |

### Learn Mode

| Command | Description |
|---------|-------------|
| `fresh learn init <name>` | Create learning project |
| `fresh learn explore <topic>` | Discover sub-topics |
| `fresh learn chapter <project>/<ch>` | Create chapter |
| `fresh learn add <path>` | Add content |
| `fresh learn link <path1> <path2>` | Link concepts |
| `fresh learn tree <project>` | Show structure |

## Documentation

- **[SPEC.md](SPEC.md)** - Full specification
- **[THEORETICAL.md](THEORETICAL.md)** - Handling theoretical topics

## License

MIT
