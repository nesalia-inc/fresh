# Fresh Guide Workflow

A complete workflow for creating and managing documentation guides with fresh.

## Overview

Fresh allows you to:
- Search documentation (local or remote)
- Save search results as persistent guides
- Manage and organize guides for quick reference

## Prerequisites

Ensure fresh is installed:
```bash
pip install fresh-docs
```

## Step-by-Step Workflow

### Step 1: Add Documentation Source

Add an alias for the documentation you want to search:

```bash
# Add React documentation
fresh alias add react https://react.dev

# Add Python documentation
fresh alias add python https://docs.python.org/3/

# Add any other documentation
fresh alias add <name> <url>
```

### Step 2: Synchronize Documentation

Download documentation for offline use and build a search index for faster searches:

```bash
# Sync with search index (recommended for faster local searches)
fresh sync react --with-index --max-pages 100

# Or sync without index
fresh sync react --max-pages 100
```

**Flags:**
- `--with-index`: Build search index after sync for faster local searches
- `--max to download (default: -pages`: Maximum pages100)
- `--check`: Only check if docs are synced, don't sync
- `--auto-sync`: Automatically sync if not available locally

## Comparing Search vs Get

Use `search` for discovering content, `get` for retrieving detailed pages:

| Command | Purpose | Output |
|---------|---------|--------|
| `fresh search` | Find pages by keyword | Results with snippets |
| `fresh get` | Fetch specific page content | Full Markdown |

**When to use `get`:**
- Creating in-depth courses or tutorials
- Needing complete page content (not just snippets)
- Building comprehensive guides from documentation
- When you know the exact URL you need

### Using Get

```bash
# Fetch a specific page (local-first by default)
fresh get https://react.dev/reference/react/useState --local

# Force remote fetch
fresh get https://react.dev/reference/react/useState --remote

# Fetch and save as guide directly
fresh get https://react.dev/reference/react/useState --remote --save-guide react-usestate

# Output to file
fresh get https://react.dev/reference/react/useState --remote --output useState.md

# Fetch multiple URLs
fresh get https://react.dev/reference/react/useState https://react.dev/reference/react/useEffect --remote
```

**Get Options:**
- `--local`: Use only local synced content
- `--remote`: Force remote fetching
- `--output`, `-o`: Write to file
- `--save-guide`: Save as guide
- `--verbose`: Show progress
- `--timeout`: Request timeout (default: 30s)

### Step 4: Create a Guide

**Option A: Save Search Results**

Use `--save-guide` with search to save results quickly:

```bash
# Quick save from search
fresh search "useState" react --local --save-guide useState-guide
```

**Option B: Fetch Detailed Content with Get**

For in-depth guides, use `get` to fetch full page content:

```bash
# Fetch specific pages
fresh get https://react.dev/reference/react/useState --remote --save-guide react-usestate
fresh get https://react.dev/learn/state-a-component-s-memory --remote --save-guide react-state-basics

# Export to files, then combine
fresh get https://react.dev/reference/react/useState --remote --output react-usestate.md
fresh get https://react.dev/reference/react/useEffect --remote --output react-useeffect.md
```

**Option C: Create Manually**

Create a guide with custom content:

```bash
fresh guide create useState-guide \
  --title "Understanding useState in React" \
  --content "# useState Guide

## Basic Usage

\`\`\`jsx
const [state, setState] = useState(initialValue);
\`\`\`

## Key Points

1. Returns a stateful value and a function to update it
2. Initial value can be any type
3. Re-renders component when state changes
" \
  --source-url "https://react.dev" \
  --tags "react,javascript,hooks"
```

**Create Options:**
- `--content`, `-c`: Guide content (markdown)
- `--title`, `-t`: Guide title (defaults to name)
- `--source-url`, `-u`: Source URL where content came from
- `--tags`: Comma-separated tags

### Step 5: Manage Guides

```bash
# List all guides
fresh guide list

# Show a specific guide
fresh guide show useState-guide

# Search within guides
fresh guide search "state"

# Update guide content
fresh guide update useState-guide --content "New content..."

# Append content to guide
fresh guide append useState-guide --content "Additional notes..."

# Export guide to file
fresh guide export useState-guide --output useState.md

# Import guide from file
fresh guide import useState.md --name useState-imported

# Delete a guide
fresh guide delete useState-guide
```

### Step 6: Clean Up (Optional)

Remove synced documentation if no longer needed:

```bash
# Note: There's no built-in delete command for synced docs
# You can manually delete the directory:
# Windows: rmdir /s C:\Users\<user>\.fresh\docs\react_dev
# Linux/Mac: rm -rf ~/.fresh/docs/react_dev
```

## Common Workflows

### Workflow 1: Quick Reference Guide

1. Sync docs: `fresh sync react --with-index`
2. Search: `fresh search "useState" react --local`
3. Save: `fresh search "useState" --save-guide useState-quickref`

### Workflow 2: Learning Guide

1. Sync with more pages: `fresh sync react --with-index --max-pages 200`
2. Search multiple topics: `fresh search "useEffect" react --local`
3. Create manual guide with notes

### Workflow 3: Multi-Source Guide

1. Sync multiple docs:
   ```bash
   fresh sync react --with-index
   fresh sync python --with-index
   ```
2. Search across sources:
   ```bash
   fresh search "function" react python --local
   ```
3. Save combined guide

### Workflow 4: In-Depth Course (Recommended)

For comprehensive courses, use `get` instead of `search`:

1. **Find relevant pages** (discover URLs):
   ```bash
   fresh search "useState" react --remote
   fresh search "QueryClient" tanstack-query --remote
   fresh search "createStore" zustand --remote
   ```

2. **Fetch detailed content** (get full pages):
   ```bash
   # React
   fresh get https://react.dev/reference/react/useState --remote --output react-usestate.md
   fresh get https://react.dev/learn/state-a-component-s-memory --remote --output react-state.md

   # TanStack Query
   fresh get https://tanstack.com/query/latest/docs/framework/react/overview --remote --output tq-overview.md

   # Zustand
   fresh get https://docs.pmnd.rs/zustand/getting-started/introduction --remote --output zustand-intro.md
   ```

3. **Create consolidated guide**:
   ```bash
   fresh guide create state-management-course \
     --title "Complete State Management Guide" \
     --content "# State Management Course

## Part 1: React useState
$(cat react-usestate.md)

## Part 2: TanStack Query
$(cat tq-overview.md)

## Part 3: Zustand
$(cat zustand-intro.md)
" \
     --tags "react,state,hooks,tanstack-query,zustand"
   ```

4. **Or use --save-guide with get**:
   ```bash
   fresh get https://react.dev/reference/react/useState --remote --save-guide react-usestate
   fresh get https://react.dev/learn/state-a-component-s-memory --remote --save-guide react-state
   # Then combine manually
   fresh guide append react-usestate --content "$(fresh guide show react-state)"
   ```

**Why get is better for courses:**
- Full page content, not just snippets
- Better quality for learning material
- Precise control over sources
- Complete code examples

## Tips

- **Use `--with-index`** when syncing for significantly faster local searches
- **Use `--auto-sync`** with search to automatically download docs if not available
- **Use `--verbose`** to see search progress
- **Use tags** to organize and filter guides
- **Export guides** to share with team or backup

## Troubleshooting

### "No local results, falling back to remote"

Run sync first: `fresh sync <alias> --with-index`

### Search is slow

Build the index: `fresh index build <alias>` or re-sync with `--with-index`

### "No sitemap found"

Some sites don't have sitemaps. Use crawler fallback: `fresh search <query> <url> --remote`

## Related Commands

| Command | Description |
|---------|-------------|
| `fresh sync` | Download documentation |
| `fresh search` | Search documentation (discover) |
| `fresh get` | Fetch page content (deep dive) |
| `fresh guide` | Manage guides |
| `fresh index` | Manage search indexes |
| `fresh alias` | Manage URL aliases |
