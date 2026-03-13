# Fresh

> A CLI tool to build and manage knowledge for coding.

Fresh helps you:
1. **Sync documentation** - Get docs locally for offline use
2. **Learn iteratively** - Build structured knowledge with a queue system

## Install

```bash
pip install fresh-docs
```

## Quick Start

```bash
# Get docs locally
fresh sync zod
fresh sync react

# Search in docs
fresh search "email validation" zod

# Start learning
fresh learn init probability-theory
fresh learn explore probability
fresh learn add probability-theory fundamentals --priority high
fresh learn next
```

## Two Things

### 1. Documentation

```bash
fresh get <url>            # Fetch a single page
fresh list <url>           # List available pages
fresh sync <topic>         # Fetch docs locally
fresh search <query>      # Search in synced docs
fresh websearch <query>   # Search the web
fresh knowledge list       # Show available docs
```

### 2. Guides

```bash
fresh guide create <name>  # Create guide
fresh guide list          # List guides
fresh guide show <name>   # Show guide
```

### 3. Learn

```bash
fresh learn init <topic>           # Start project
fresh learn explore <topic>        # Discover concepts
fresh learn add <concept> --priority high|medium|low  # Add to queue
fresh learn queue                  # View queue
fresh learn next                  # Get next concept
fresh learn start <concept>       # Start learning
fresh learn done <concept>        # Mark complete
fresh learn link <a> <b>         # Link concepts
```

## Structure

```
.fresh/
├── knowledge/           # Synced documentation
└── learning/           # Learning projects
```

## Why

AI agents (and humans) need to:
- Have docs available offline
- Build structured knowledge over time
- Track what to learn next

Fresh makes this easy.

## License

MIT
