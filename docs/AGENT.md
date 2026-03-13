# Fresh Agent Behavior

## Overview

The Fresh Agent is the brain of Fresh V2. It orchestrates fetching, analysis, and guide generation to provide end agents with relevant, up-to-date knowledge.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Fresh Agent                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Intent    │  │  Knowledge  │  │  Synthesis │        │
│  │  Parser    │  │  Engine     │  │  Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Intent Parser

Analyzes the incoming request to determine:
- What the user wants (learn, fetch, search, create)
- Which topics/technologies are involved
- What version or focus area is relevant
- Urgency and depth requirements

### Knowledge Engine

Manages the knowledge base:
- Check existing knowledge
- Determine freshness of content
- Decide what needs to be fetched
- Maintain version history

### Synthesis Engine

Generates output:
- Analyze fetched documentation
- Generate Markdown guides
- Extract code examples
- Create comparisons/versions

## Decision Flow

```
User Request
     │
     ▼
┌─────────────────┐
│  Intent Parser  │
│  - What?        │
│  - Topics?      │
│  - Version?     │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Knowledge      │
│  Check          │
│  - Have it?     │
│  - Fresh?       │
└─────────────────┘
     │
     ├── YES + FRESH ──▶ Return existing
     │
     ├── YES + STALE ──▶ Fetch update → Generate
     │
     └── NO ──────────▶ Fetch → Analyze → Generate
     │
     ▼
┌─────────────────┐
│  Synthesis      │
│  - Analyze docs │
│  - Generate MD  │
│  - Store        │
└─────────────────┘
     │
     ▼
   Output (Markdown)
```

## Intent Types

### Learn Intent

```
"learn zod"
"teach me about react hooks"
"give me a guide on next.js auth"
```

**Action:**
1. Check if topic exists in knowledge base
2. If yes, check freshness
3. If stale/missing, fetch docs
4. Generate comprehensive guide
5. Store and return

### Fetch Intent

```
"fetch zod docs"
"sync https://docs.python.org"
"update react"
```

**Action:**
1. Fetch documentation
2. Store in knowledge base
3. Return metadata (not full guide)

### Search Intent

```
"search zod validation"
"how do i validate email in zod"
```

**Action:**
1. Query knowledge base
2. Return relevant sections
3. Optionally suggest guide generation

### Create Intent

```
"create guide my-project"
"make a guide on testing"
```

**Action:**
1. Get user content
2. Format as Markdown
3. Store in guides
4. Return confirmation

## Topic Detection

### Explicit

User mentions topic directly:
```
"learn zod" → topic: "zod"
"next.js auth" → topic: "next.js", focus: "auth"
```

### Implicit

User mentions without naming:
```
"validate user input" → detect: "zod", "validation"
"handle state" → detect: "react", "state-management"
```

**Detection methods:**
1. Keyword matching
2. Code pattern analysis
3. Common library signatures

## Version Handling

### Version Extraction

From request:
```
"zod v4" → version: "v4"
"react 18" → version: "18"
```

Detected from code:
```typescript
// User shows code
import { z } from "zod"
// Detect: zod, guess latest version
```

### Version Comparison

Fresh can compare versions:

```
Request: "zod v3 vs v4"
Action:
1. Fetch both versions if needed
2. Generate comparison guide
3. Return diff

Output:
# Zod v3 → v4 Migration

## Changes
- `z.string().email()` → `z.email()`
- ...
```

## Guide Generation

### Synthesis Prompts

When generating a guide, Fresh uses structured prompts:

```
Topic: {topic}
Version: {version}
Focus: {focus}
Audience: "AI Agent"

Generate a Markdown guide that:
1. Summarizes key concepts
2. Shows common patterns
3. Highlights changes if version specified
4. Includes practical code examples
```

### Guide Structure

```markdown
# {Topic} - {Focus}

## Overview
{Brief summary of what this is about}

## Key Concepts
- {Concept 1}
- {Concept 2}
- ...

## Practical Patterns

### {Pattern Name}
```language
// Code example
```

## Common Use Cases

### {Use Case}
How to handle...

## Best Practices
- {Tip 1}
- {Tip 2}

## Related Topics
- {Related topic 1}
- {Related topic 2}
```

## Freshness Management

### TTL (Time To Live)

Each piece of knowledge has a freshness window:

| Topic Type | Default TTL |
|------------|-------------|
| Core tools (React, TypeScript) | 24 hours |
| Stable libs | 7 days |
| Beta/RC | 1 hour |
| User guides | 30 days |

### Freshness Check

```
is_fresh(topic, version):
  last_update = get_last_updated(topic, version)
  ttl = get_ttl(topic)

  if now - last_update > ttl:
    return False
  return True
```

### Update Triggers

- Manual: `fresh update <topic>`
- On use: If stale, fetch in background
- Scheduled: Cron job for critical topics

## Error Handling

### Fetch Failures

```
If fetch fails:
  1. Try alternative source
  2. If all fail → return error + cached version
  3. Suggest manual intervention
```

### Generation Failures

```
If generation fails:
  1. Return raw fetched content
  2. Log for debugging
  3. Offer simplified guide
```

### Partial Knowledge

```
If partial knowledge exists:
  1. Return what we have
  2. Indicate what's missing
  3. Offer to fetch missing parts
```
