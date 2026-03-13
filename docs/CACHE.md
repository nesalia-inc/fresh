# Cache System

Fresh uses an internal cache to avoid repeated requests.

## What's Cached

- Web search results
- Fetched documentation pages
- Explore results

## How It Works

```bash
# First search - fetches from web
fresh websearch "react hooks"
# → Caches result

# Second search - returns cached
fresh websearch "react hooks"
# → Returns cached result (fast)

# Force refresh
fresh websearch "react hooks" --no-cache
```

## Cache Location

```
.fresh/
├── cache/
│   ├── websearch/
│   │   └── {hash}.json
│   ├── docs/
│   │   └── {topic}/
│   └── explore/
│       └── {topic}.json
└── ...
```

## TTL (Time To Live)

| Type | Default TTL |
|------|-------------|
| Web search | 24 hours |
| Docs | 7 days |
| Explore | 24 hours |

## Commands

```bash
# Clear all cache
fresh cache clear

# Clear specific
fresh cache clear websearch
fresh cache clear docs
fresh cache clear explore

# Show cache status
fresh cache status
```
