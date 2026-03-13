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
# Fetch a single page
fresh get <url>
fresh get <url> -o <file>
fresh get <url> --no-cache

# List available pages
fresh list <url>
fresh list <url> --depth <n>
fresh list <url> --json
fresh list <url> --pattern <regex>

# Fetch docs locally
fresh sync <url>
fresh sync <url> --depth <n>
fresh sync <url> --force
fresh sync <url> -o <directory>

# Search in synced docs
fresh search <query>
fresh search <query> <topic>
fresh search <query> --no-cache

# Search the web
fresh websearch <query>
fresh websearch <query> --count <n>
fresh websearch <query> --json
fresh websearch <query> --table
fresh websearch <query> --no-cache

# Show available docs
fresh knowledge list
```

### 2. Guides

```bash
# Create guide (folder structure)
fresh guide create <name>

# Add file to guide
fresh guide add <guide>/<file>
fresh guide add <guide>/<file> --content "<markdown>"

# List guides
fresh guide list

# Show guide
fresh guide show <name>
```

### 3. Learn

```bash
# Start learning project
fresh learn init <topic>
fresh learn init <topic> --description <text>

# Discover concepts
fresh learn explore <topic>
fresh learn explore <topic> --depth <n>

# Add to queue
fresh learn add <project> <concept>
fresh learn add <project> <concept> --priority high|medium|low
fresh learn add <project> <concept> --from <source>

# View queue
fresh learn queue <project>

# Get next concept
fresh learn next <project>

# Start learning
fresh learn start <project>/<concept>

# Mark complete
fresh learn done <project>/<concept>

# Link concepts
fresh learn link <project>/<a> <project>/<b>
```

### 4. Registry

```bash
# Pull a guide from community
fresh registry pull @account/guide-name

# Search community guides
fresh registry search <query>

# List trending guides
fresh registry trending

# Publish your guide
fresh registry publish <guide-name>

# Your published guides
fresh registry my-guides
```

### 5. Cache

```bash
# Clear cache
fresh cache clear
fresh cache clear websearch
fresh cache clear docs

# Show cache status
fresh cache status
```

## Structure

```
.fresh/
├── knowledge/           # Synced documentation
│   └── zod/
│       └── docs/
├── guides/             # Guides
│   └── optimistic-state/
└── learning/           # Learning projects
    └── probability-theory/
```

## Why

AI agents (and humans) need to:
- Have docs available offline
- Build structured knowledge over time
- Track what to learn next

Fresh makes this easy.

## License

MIT
