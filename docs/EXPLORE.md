# Explore Command

> Intelligent concept discovery for learning projects.

## Purpose

The `fresh learn explore` command returns **concepts to deepen** - not just a list, but an intelligent discovery of what to learn next.

## What It Returns

```bash
fresh learn explore probability
```

Returns:
```json
{
  "topic": "probability",
  "concepts": [
    {
      "name": "fundamentals",
      "description": "Basic concepts: sample space, events, probability function",
      "depth": 1,
      "prerequisites": []
    },
    {
      "name": "conditional",
      "description": "Conditional probability, Bayes theorem",
      "depth": 2,
      "prerequisites": ["fundamentals"]
    },
    {
      "name": "distributions",
      "description": "Probability distributions: discrete and continuous",
      "depth": 2,
      "prerequisites": ["fundamentals"]
    },
    {
      "name": "random-variables",
      "description": "Random variables, expected value, variance",
      "depth": 3,
      "prerequisites": ["fundamentals", "distributions"]
    }
  ],
  "suggested_order": [
    "fundamentals",
    "conditional",
    "distributions",
    "random-variables"
  ]
}
```

## How It Works

### For Technical Topics (synced docs)

When docs are synced, explore analyzes them:

```bash
fresh sync zod
fresh learn explore zod
```

Returns concepts discovered from the documentation structure:
- API sections
- Tutorials
- Guides

### For Theoretical Topics (web search)

When no docs exist, explore uses web search:

```bash
fresh learn explore probability
→ Web search for "probability theory topics"
→ Analyze results
→ Return concept suggestions
```

### Mixed Approach

```bash
fresh learn explore react
→ Use synced React docs
→ Also search for "React patterns best practices"
→ Combine results
```

## Command Variations

### Explore main topics

```bash
fresh learn explore probability
# Returns: [fundamentals, distributions, statistics, bayes]
```

### Explore specific chapter

```bash
fresh learn explore probability/fundamentals
# Returns: [sample-space, events, probability-function]
```

### Explore with depth

```bash
fresh learn explore probability --depth 2
# Returns top 2 levels of concepts
```

### Get suggestions for project

```bash
fresh learn suggestions my-project
# Returns: what concepts are missing, what's next
```

## Output Format

### Basic (CLI)

```
📚 Probability Theory

Suggested concepts:
1. fundamentals (depth 1) - Basic concepts
2. conditional (depth 2) - Conditional probability
3. distributions (depth 2) - Probability distributions
4. random-variables (depth 3) - Random variables

Next: start with "fundamentals"
```

### JSON (for agents)

```bash
fresh learn explore probability --json
```

```json
{
  "topic": "probability",
  "concepts": [...],
  "suggested_order": [...],
  "next": "fundamentals"
}
```

## Integration with Learning

Explore feeds directly into the learning workflow:

```bash
# 1. Explore what to learn
fresh learn explore probability

# 2. See suggestions
# fundamentals → conditional → distributions → ...

# 3. Start with first suggestion
fresh learn chapter probability 01-fundamentals

# 4. Add content
fresh learn add probability/01-fundamentals/sample-space --content "..."

# 5. Explore next level
fresh learn explore probability/fundamentals
# → Returns: [sample-space, events, probability-function]

# 6. Continue...
```

## Smart Features

### Dependency Tracking

```bash
fresh learn explore machine-learning
# Returns concepts with prerequisites:
# - linear-algebra → (prerequisite: none)
# - probability → (prerequisite: linear-algebra)
# - neural-networks → (prerequisite: linear-algebra, probability)
```

### Gap Analysis

```bash
fresh learn suggestions my-project
# Analyzes what exists vs what's suggested
# Returns:
# - ✅ Completed: fundamentals, sample-space
# - ⏳ In progress: conditional
# - ❌ Missing: distributions, random-variables
```

### Adaptive Suggestions

```bash
fresh learn next my-project
# Based on:
# - What's already covered
# - Prerequisites of uncovered topics
# - Suggested order
# Returns: "Next: learn 'conditional probability'"
```
