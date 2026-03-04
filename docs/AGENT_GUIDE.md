# Fresh CLI - Agent Guide

## Purpose

**Fresh** is designed to help AI agents and CLI tools fetch documentation from any website and store it locally for fast, offline access. The primary workflow is:

1. **Check** - Verify if documentation is already available locally
2. **Sync** - Download all documentation pages if not available
3. **Search/Read** - Access local content instantly without network calls

This approach dramatically improves performance for AI agents that need to reference documentation frequently.

## Installation

```bash
# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Core Workflow for Agents

### Step 1: Check Local Availability First

**ALWAYS check if documentation exists locally before any operation:**

```bash
# Check if sync metadata exists (documentation is available locally)
# The sync directory is: ~/.fresh/docs/<domain>/

# Method 1: Try a sync with --check flag (if supported)
fresh sync https://docs.python.org/3/ --check

# Method 2: Check if sync directory exists and has content
ls ~/.fresh/docs/docs_python_org_3/
# If directory exists and contains pages/ folder → already synced
```

If documentation is NOT available locally → proceed to Step 2.
If documentation IS available locally → proceed to Step 3.

### Step 2: Sync If Needed

If not available locally, sync the documentation:

```bash
# Sync all pages from a documentation site
fresh sync https://docs.python.org/3/

# With custom output directory
fresh sync https://docs.python.org/3/ -o ./docs/python

# Force re-sync to update content
fresh sync https://docs.python.org/3/ -f
```

**Why check first?**
- Avoids unnecessary network calls
- Instant response when docs are available locally
- Only downloads what you need

### Step 3: Search Local Content

After confirming local availability, search the local index:

```bash
# Search within synced documentation
fresh search "virtual environment" https://docs.python.org/3/
fresh search "class definition" https://docs.python.org/3/
```

### Step 4: Get Specific Pages

Retrieve specific pages from local storage:

```bash
# Get a page and save to file
fresh get https://docs.python.org/3/tutorial/ -o ./docs/python/tutorial.md
```

## Agent Decision Tree

```
START
  │
  ▼
Check: Does ~/.fresh/docs/<domain>/_sync.json exist?
  │
  ├─── YES ──▶ Use local (search/get)
  │
  └─── NO ──▶ Run: fresh sync <URL>
                    │
                    ▼
               Verify sync worked
               (check _sync.json exists)
                    │
                    ▼
               Use local (search/get)
```

## Commands Reference

### `fresh sync`

Download entire documentation for offline use.

```bash
fresh sync <URL> [OPTIONS]

# Options
--check                   # Only check if already synced, don't sync
-o, --output-dir PATH    # Target directory for synced docs
-v, --verbose           # Show progress
--max-pages INTEGER      # Max pages to download (default: 100)
-d, --depth INTEGER     # Crawl depth (default: 3)
-f, --force             # Delete existing and re-sync
-p, --pattern TEXT      # Filter paths matching pattern
```

### `fresh search`

Search within synced documentation.

```bash
fresh search <QUERY> <URL> [OPTIONS]

# Options
-v, --verbose           # Show more details
-l, --limit INTEGER     # Max results (default: 20)
```

### `fresh get`

Fetch a specific page (uses local cache if available).

```bash
fresh get <URL> [OPTIONS]

# Options
-o, --output TEXT       # Save to file
-v, --verbose          # Show details
--no-cache             # Force re-download
--dry-run              # Preview without downloading
```

### `fresh alias`

Create shortcuts for frequently accessed documentation.

```bash
# Add alias
fresh alias add python https://docs.python.org/3/

# List aliases
fresh alias list
```

## Agent Usage Patterns

### Pattern 1: Always Check First

```bash
# Check if already synced by testing sync metadata file
SYNC_DIR="$HOME/.fresh/docs/docs_python_org_3"

if [ -f "$SYNC_DIR/_sync.json" ]; then
    # Already synced - use local search
    fresh search "virtual environment" https://docs.python.org/3/
else
    # Not synced - sync first
    fresh sync https://docs.python.org/3/
    fresh search "virtual environment" https://docs.python.org/3/
fi
```

### Pattern 2: Initial Setup

```bash
# Agent startup: sync all needed documentation
fresh sync https://docs.python.org/3/ -o ~/.fresh/docs/python
fresh sync https://docs.rust-lang.org/ -o ~/.fresh/docs/rust
```

### Pattern 3: On-Demand Sync

```bash
# When user asks about a new topic
SYNC_DIR="$HOME/.fresh/docs/$(echo <unknown-url> | sed 's/[^a-zA-Z0-9]/_/g')"

if [ ! -f "$SYNC_DIR/_sync.json" ]; then
    fresh sync <unknown-url> --max-pages 50
fi

fresh search "<topic>" <unknown-url>
```

### Pattern 4: Verify Before Search

```bash
# Always verify first
SYNC_DIR="$HOME/.fresh/docs/docs_python_org_3"

if [ -f "$SYNC_DIR/_sync.json" ]; then
    # Fast local search
    fresh search "virtual environment" https://docs.python.org/3/
else
    echo "Documentation not available locally. Run: fresh sync https://docs.python.org/3/"
fi
```

## Local Storage Location

Synced documentation is stored in:

```
~/.fresh/docs/<domain>/
├── _sync.json          # Sync metadata (site, last_sync, page_count)
└── pages/
    ├── index.html
    ├── tutorial.html
    └── ...
```

### Checking Sync Status

```bash
# List all synced sites
ls ~/.fresh/docs/

# Check specific site metadata
cat ~/.fresh/docs/docs_python_org_3/_sync.json

# Check page count
cat ~/.fresh/docs/docs_python_org_3/_sync.json | jq .page_count
```

## Performance Notes

| Operation | Without Sync | With Sync |
|-----------|--------------|-----------|
| Check availability | ~500ms | ~10ms (file check) |
| Search | ~2-5s (network) | ~50ms (local) |
| Get page | ~1-3s (network) | ~10ms (local) |
| Offline | Not possible | Works fully |

**Golden Rule**: Check if `_sync.json` exists first. If pages exist locally, all subsequent operations are nearly instantaneous.

## Troubleshooting

### "Documentation not available locally"
```bash
# Check what's in the docs directory
ls ~/.fresh/docs/

# Try to sync
fresh sync <URL>
```

### No search results
```bash
# Verify sync exists
ls -la ~/.fresh/docs/<domain>/_sync.json

# If not, sync first
fresh sync <URL>
```

### Outdated content
```bash
# Force fresh sync
fresh sync <URL> -f

# Verify it worked
cat ~/.fresh/docs/<domain>/_sync.json
```

### Permission errors
```bash
# Check directory permissions
ls -la ~/.fresh/docs/
```
