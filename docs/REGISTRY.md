# Registry

> Community guides - pull guides from other users.

## Concept

Share and discover guides from the community:

```
@account/guide-name
```

## Commands

### Auth

```bash
# Login (opens browser for OAuth2)
fresh auth login

# Logout
fresh auth logout

# Show current user
fresh auth whoami
```

### Organizations

```bash
# Create organization
fresh org create mycompany

# List your organizations
fresh org list

# Add member
fresh org add-member mycompany @john

# Invite user
fresh org invite mycompany user@email.com

# Remove member
fresh org remove-member mycompany @john
```

### Registry

```bash
# Pull a guide
fresh registry pull @martty-code/zustand-best-practices
fresh registry pull @mycompany/backend-guides

# Search community guides
fresh registry search "react hooks"
fresh registry search "state management"

# List trending guides
fresh registry trending

# Publish your guide
fresh registry publish my-guide
fresh registry publish @mycompany/frontend-standards

# Your published guides
fresh registry my-guides

# Organization guides
fresh registry org-guides @mycompany
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
| Pull community guides | ⏳ (25 guides) | ✅ unlimited |
| Publish guides | ✅ | ✅ |
| Featured guides (promoted) | ❌ | ✅ |

## Types of Guides

```
@react/hooks-guide           ← OFFICIAL (from React team)
@john-doe/react-patterns    ← FEATURED (promoted)
@random-user/guide          ← COMMUNITY (normal)
```

### Official
- From the team behind the library
- Badge ✅
- Shown at top
- Free for maintainers

### Featured
- Promoted by paying
- Badge 🌟
- Shown after official, before community

### Community
- Regular guides from users
- Ranked by popularity

## Popularity

Guides are ranked by popularity (pulls):

```
fresh registry trending

# Results:
✅ @react/hooks-guide            (OFFICIAL)
🌟 @john-doe/react-patterns     (1,234 pulls)
   @jane-smith/zod-mastery      (987 pulls)
   @random-user/guide           (456 pulls)
```

- **Official** = shown first (free for maintainers)
- **Featured** = promoted (paid)
- **Popularity** = based on pulls (automatic)

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
