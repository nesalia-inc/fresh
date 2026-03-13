# Registry

> Community guides - pull guides from other users.

## Concept

Share and discover guides from the community:

```
@account/guide-name
```

## Commands

```bash
# Pull a guide from community
fresh registry pull @martty-code/zustand-best-practices

# Search community guides
fresh registry search "react hooks"
fresh registry search "state management"

# List trending guides
fresh registry trending

# Publish your guide
fresh registry publish optimistic-state
fresh registry publish @my-account/optimistic-state

# Your published guides
fresh registry my-guides
```

## Structure

```
fresh registry pull @account/guide-name
    │         │           │
    │         │           └── Guide name
    │         └── Account/username
    └── Registry namespace
```

## Access

| Action | Free | Paid |
|--------|------|------|
| Pull community guides | ✅ | ✅ |
| Publish guides | ✅ | ✅ |
| Featured guides | ✅ | ✅ |

**Paid is just to cover hosting costs, not to make profit.**

## Example

```bash
# User publishes their guide
fresh registry publish my-react-patterns

# Other users pull it
fresh registry pull @username/my-react-patterns

# Now available locally
.fresh/guides/my-react-patterns/
```

## Use Cases

- Discover best practices from others
- Share your learning projects
- Get started quickly with curated guides
- Build on top of existing guides
