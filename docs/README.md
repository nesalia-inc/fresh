# Fresh Documentation

## Overview

Fresh is a CLI tool that helps you build and manage knowledge for coding.

## Docs

| File | Description |
|------|-------------|
| [PROJECT.md](PROJECT.md) | Project overview and vision |
| [SPEC.md](SPEC.md) | Full specification |
| [THEORY.md](THEORY.md) | Theory vs implementations |
| [THEORETICAL.md](THEORETICAL.md) | Learning theoretical topics |
| [SYNC.md](SYNC.md) | Step 1: Documentation sync |
| [GUIDES.md](GUIDES.md) | Guide structure (folders/files) |
| [EXPLORE.md](EXPLORE.md) | Explore command |
| [AGENT.md](AGENT.md) | Fresh is a CLI for everyone |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture |
| [CACHE.md](CACHE.md) | Internal cache system |
| [REGISTRY.md](REGISTRY.md) | Community guides |

## Two Things

1. **Sync docs** - Fetch documentation locally
2. **Learn** - Build knowledge iteratively

## Commands

### Documentation

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
fresh list <url> --no-cache

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

### Guides

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

### Learning

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

### Registry

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

### Cache

```bash
# Clear cache
fresh cache clear
fresh cache clear websearch
fresh cache clear docs

# Show cache status
fresh cache status
```
