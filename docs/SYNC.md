# Step 1: Documentation Sync

> The core of Fresh: get documentation, keep it local, keep it fresh.

## Why

AI agents need access to up-to-date documentation. But:
- Docs change often
- Online docs can be slow or unavailable
- Agents need offline access

Fresh solves this by fetching docs and keeping them locally.

## The Workflow

```
1. List pages     →  discover what's available
2. Get pages     →  fetch specific pages
3. Sync site     →  fetch everything
4. Search        →  find what you need
```

---

## List

Discover all pages on a documentation site.

```bash
fresh list https://docs.zod.dev/
```

Output:
```
/
/introduction
/api/schema
/api/validators
/api/refinements
/guides/index
/guides/migration
```

Options:
```bash
fresh list https://docs.zod.dev/          # All pages
fresh list https://docs.zod.dev/ --depth 2  # Max depth
fresh list https://docs.zod.dev/ --json     # JSON output
```

---

## Get

Fetch a single page as Markdown.

```bash
fresh get https://docs.zod.dev/api/schema
```

Output:
```markdown
# Schema

## Overview

...

## Methods

### .parse()

Parses an input against a schema.

```typescript
const schema = z.string();
schema.parse("hello"); // "hello"
```
```

Options:
```bash
fresh get <url>                    # Default
fresh get <url> -o file.md         # Save to file
fresh get <url> --no-cache         # Skip cache
```

---

## Sync

Fetch entire documentation site.

```bash
fresh sync https://docs.zod.dev/
```

This:
1. Lists all pages
2. Fetches each page
3. Converts to Markdown
4. Saves to `.fresh/knowledge/zod/`

Structure after sync:
```
.fresh/knowledge/zod/
├── docs/
│   ├── introduction.md
│   ├── api/
│   │   ├── schema.md
│   │   ├── validators.md
│   │   └── refinements.md
│   └── guides/
│       ├── index.md
│       └── migration.md
└── metadata.json
```

Options:
```bash
fresh sync <url>                   # Default
fresh sync <url> --depth 3         # Max depth
fresh sync <url> --force           # Re-fetch all
fresh sync <url> -o ./my-docs/     # Custom directory
```

---

## Search

Search in local documentation.

```bash
fresh search "email validation"
```

Search specific topic:
```bash
fresh search "email validation" zod
```

---

## Use Cases

### Agent Workflow

```bash
# 1. Agent needs Zod docs
fresh sync https://docs.zod.dev/

# 2. Agent looks for specific info
fresh search "email validation" zod

# 3. Agent fetches specific page
fresh get https://docs.zod.dev/api/validators
```

### Keep Fresh

```bash
# Update existing docs
fresh sync https://docs.zod.dev/

# Only fetches changed pages
# (uses cache/ETag)
```

---

## What Makes a Good Sync

- [ ] All pages fetched
- [ ] Markdown is readable
- [ ] Code blocks preserved
- [ ] Links work (relative → local, absolute → external)
- [ ] Images handled
- [ ] Searchable

---

## Priority

This is **Step 1** - the foundation.

Fresh must first excel at:
1. `list` - discover all pages
2. `get` - fetch single page
3. `sync` - fetch entire site
4. `search` - find in local docs

Then build learning on top.
