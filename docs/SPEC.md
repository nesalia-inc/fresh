# Fresh V2 - Agent Knowledge System

## Overview

Fresh is a CLI tool to build and manage knowledge for coding.

## Step 1: Get Documentation (Core)

The foundation: list pages, fetch them, keep locally.

### List pages

```bash
fresh list https://docs.zod.dev/
# Returns: [/introduction, /api/schema, /api/validators, ...]
```

### Get pages

```bash
fresh get https://docs.zod.dev/api/schema
# Returns: Markdown content

fresh get https://docs.zod.dev/api/validators
# Returns: Markdown content
```

### Sync entire site

```bash
fresh sync https://docs.zod.dev/
# Fetches all pages, converts to Markdown
# Stores locally in .fresh/knowledge/zod/
```

### Search in docs

```bash
fresh search "email validation"
# Searches in local docs
```

---

## Step 2: Learn (Optional)

Build structured knowledge with queue system.

### Start learning

```bash
fresh learn init probability-theory
fresh learn explore probability
fresh learn add probability-theory fundamentals --priority high
fresh learn next
```

---

## All Commands

### Documentation

```bash
fresh list <url>            # List all pages
fresh get <url>             # Fetch a page
fresh sync <topic>          # Fetch entire site
fresh search <query>        # Search in local docs
fresh websearch <query>    # Search the web
```

### Learning

```bash
fresh learn init <topic>           # Start project
fresh learn explore <topic>        # Discover concepts
fresh learn add <concept> --priority high|medium|low
fresh learn queue                  # View queue
fresh learn next                   # Get next concept
fresh learn start <concept>        # Start
fresh learn done <concept>         # Complete
fresh learn link <a> <b>          # Link
```

### Cache

```bash
fresh cache clear
fresh cache status
```

---

## Structure

```
.fresh/
├── knowledge/           # Synced documentation
│   └── zod/
│       └── docs/
└── learning/           # Learning projects
```

---

## Priority

Fresh focuses on **Step 1**: getting documentation right first.
- Perfect list + get + sync
- Then build learning on top
