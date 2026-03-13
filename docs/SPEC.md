# Fresh V2 - Agent Knowledge System

## Overview

Fresh is a CLI tool that helps you build and manage knowledge for coding. It works the same way for humans and AI agents.

Two things you can do:
1. **Sync docs** - Get documentation locally for offline use
2. **Learn** - Build structured knowledge through iterative learning

```
.fresh/
├── knowledge/           # Synced documentation
│   ├── zod/
│   └── react/
└── learning/           # Learning projects
    └── probability-theory/
```

---

## Commands

### Documentation

```bash
fresh get <url>             # Fetch a single page
fresh list <url>            # List available pages
fresh sync <topic>          # Fetch docs locally
fresh search <query>        # Search in synced docs
fresh websearch <query>    # Search the web
fresh knowledge list       # Show available docs
```

### Learning

```bash
fresh learn init <topic>           # Start learning project
fresh learn explore <topic>        # Discover concepts
fresh learn add <path> --content "..."  # Add content
fresh learn queue                  # See what to learn next
fresh learn next                   # Get next concept
fresh learn start <concept>       # Start learning a concept
fresh learn done <concept>         # Mark concept as complete
fresh learn link <a> <b>          # Link concepts

### Cache

```bash
fresh cache clear           # Clear all cache
fresh cache status          # Show cache status
```

---

## Learning Workflow

### Step 1: Start

```bash
fresh learn init probability-theory
```

### Step 2: Explore

```bash
fresh learn explore probability
# Returns: [fundamentals, distributions, conditional, random-variables]
```

### Step 3: Add to Queue

```bash
fresh learn add probability-theory gaussian --priority high
fresh learn add probability-theory binomial --priority medium
```

### Step 4: Learn

```bash
fresh learn next
# → Returns: gaussian (highest priority)

fresh learn start gaussian
fresh learn add probability-theory/gaussian/definition --content "..."
fresh learn done gaussian
```

### Step 5: Iterate

```bash
# Discover more while learning
fresh learn explore probability/distributions

# Add new discoveries
fresh learn add probability-theory central-limit-theorem --priority high
```

---

## Queue System

The queue manages what to learn next:

```bash
fresh learn queue
```
```
probability-theory
├── high priority
│   └── gaussian
├── medium priority
│   ├── binomial
│   └── conditional
└── low priority
    └── random-variables
```

---

## Structure

```
.fresh/learning/probability-theory/
├── _meta/
│   └── queue.json           # Learning queue
├── 01-fundamentals/
│   ├── 01-sample-space.md
│   └── 02-events.md
└── 02-gaussian/
    └── definition.md
```

---

## Priority

| Priority | When |
|----------|------|
| high | Core concepts, prerequisites |
| medium | Standard concepts |
| low | Nice-to-have |

---

## CLI for Everyone

Fresh is a CLI tool. Both humans and AI agents use the same commands:

- **Human**: Runs commands directly
- **AI Agent**: Runs commands in its workflow

There's no special "Agent mode" - just a CLI that everyone uses.
