# Guides

> A guide is a collection of folders, subfolders, and files - like a mini-book.

## Structure

A guide is not a single file. It's a directory:

```
.fresh/guides/
└── optimistic-state/
    ├── _meta.json              # Guide metadata
    ├── 01-react-query/
    │   ├── overview.md
    │   └── code-examples.md
    ├── 02-zustand/
    │   ├── overview.md
    │   └── patterns.md
    └── 03-comparison.md
```

## Commands

```bash
# Create guide
fresh guide create optimistic-state

# Add section
fresh guide add optimistic-state/01-react-query

# Add file
fresh guide add optimistic-state/01-react-query/overview.md --content "# React Query\n\n..."

# List guides
fresh guide list

# Show guide
fresh guide show optimistic-state
```

## Guide Metadata

```json
// .fresh/guides/optimistic-state/_meta.json
{
  "name": "optimistic-state",
  "created": "2026-03-13",
  "topics": ["react", "zustand", "react-query"]
}
```

## Use

Guides are for:
- Quick references
- Personal notes
- Aggregated knowledge

They can be simple (one file) or structured (folders).
