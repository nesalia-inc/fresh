# Fresh

> A CLI tool to fetch and sync documentation locally.

## Install

```bash
pip install fresh-docs
```

## Quick Start

```bash
# List pages
fresh list https://docs.zod.dev/

# Get a page
fresh get https://docs.zod.dev/api/schema

# Sync entire site
fresh sync https://docs.zod.dev/

# Search in local docs
fresh search "email validation" zod
```

## Commands

```bash
fresh list <url>            # List all pages
fresh get <url>             # Fetch a page as Markdown
fresh sync <url>            # Sync entire site locally
fresh search <query>       # Search in local docs
fresh websearch <query>    # Search the web
```

## Structure

```
.fresh/
└── knowledge/
    └── zod/
        └── docs/
```

## Why

Keep documentation locally:
- Offline access
- Always available
- Up-to-date

## License

MIT
