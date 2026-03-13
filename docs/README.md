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
| [EXPLORE.md](EXPLORE.md) | Explore command |
| [AGENT.md](AGENT.md) | Fresh is a CLI for everyone |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture |

## Two Things

1. **Sync docs** - Fetch documentation locally
2. **Learn** - Build knowledge iteratively

## Quick Start

```bash
fresh sync zod
fresh learn init probability-theory
```

## Commands

### Documentation

```bash
fresh sync <topic>           # Fetch docs locally
fresh search <query>         # Search in synced docs
```

### Learning

```bash
fresh learn init <topic>           # Start project
fresh learn explore <topic>        # Discover concepts
fresh learn add <concept> --priority high|medium|low  # Add to queue
fresh learn queue                  # View queue
fresh learn next                   # Get next concept
fresh learn start <concept>        # Start learning
fresh learn done <concept>         # Mark complete
```
