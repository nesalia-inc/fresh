# Concept Queue

> Priority queue for learning concepts with learn concept add/next/start/complete.

## Overview

The concept queue is a **priority-based learning queue** that manages what concepts to learn next.

```
.fresh/learning/probability-theory/_meta/queue.json
```

## Commands

### Add Concept

```bash
fresh learn concept add <project> <concept> [options]

Options:
  --priority high|medium|low     # Priority level (default: medium)
  --from <concept>              # Discovered from which concept
  --description "<text>"        # Description
```

Examples:

```bash
# Add from exploration
fresh learn concept add probability-theory gaussian \
  --from distributions \
  --priority high

# Add manually
fresh learn concept add probability-theory central-limit-theorem \
  --priority high \
  --description "Important for statistics"

# Add multiple
fresh learn concept add probability-theory \
  binomial poisson exponential \
  --priority medium
```

### View Queue

```bash
fresh learn concept queue <project>
```

Output:
```
📚 probability-theory - Concept Queue

Priority: high
├── [ ] central-limit-theorem (needs: gaussian)
├── [ ] gaussian (needs: none)

Priority: medium
├── [ ] binomial (from: distributions)
├── [ ] poisson (from: distributions)
└── [ ] exponential (from: distributions)

Priority: low
└── [ ] markov-chains

Currently learning: conditional
```

### Get Next

```bash
fresh learn concept next <project>
```

Returns the next concept to learn based on:
- Priority (high → medium → low)
- Prerequisites met
- Dependencies resolved

Output:
```
Next: gaussian (priority: high)
Prerequisites: ✅ none
Ready to start? Yes
```

### Start Concept

```bash
fresh learn concept start <project>/<concept>
```

Marks a concept as "in progress":

```bash
fresh learn concept start probability-theory/gaussian

# Output:
# 🎯 Started learning: gaussian
# Status: in_progress
# Location: .fresh/learning/probability-theory/03-distributions/01-gaussian/
```

### Complete Concept

```bash
fresh learn concept complete <project>/<concept>
```

Marks as completed and suggests next:

```bash
fresh learn concept complete probability-theory/gaussian

# Output:
# ✅ Completed: gaussian
#
# Next suggestions:
# 1. central-limit-theorem (priority: high, now ready!)
# 2. binomial (priority: medium)
```

## Queue Structure

```json
// .fresh/learning/probability-theory/_meta/queue.json
{
  "project": "probability-theory",
  "current": "conditional",
  "queue": [
    {
      "id": "gaussian",
      "name": "Gaussian Distribution",
      "priority": "high",
      "status": "pending",
      "prerequisites": [],
      "discovered_from": "distributions",
      "created_at": "2026-03-13T10:00:00Z"
    },
    {
      "id": "binomial",
      "name": "Binomial Distribution",
      "priority": "medium",
      "status": "pending",
      "prerequisites": [],
      "discovered_from": "distributions",
      "created_at": "2026-03-13T10:00:00Z"
    },
    {
      "id": "central-limit-theorem",
      "name": "Central Limit Theorem",
      "priority": "high",
      "status": "pending",
      "prerequisites": ["gaussian"],
      "discovered_from": "gaussian",
      "created_at": "2026-03-13T10:01:00Z"
    }
  ],
  "completed": [
    "fundamentals",
    "sample-space",
    "events"
  ]
}
```

## Priority Flow

```
1. fresh learn explore probability
   → discovers: [fundamentals, distributions, conditional]

2. fresh learn concept add probability-theory fundamentals --priority high

3. fresh learn concept add probability-theory distributions --priority medium

4. fresh learn concept next probability-theory
   → returns: "fundamentals" (highest priority)

5. fresh learn concept start probability-theory/fundamentals
   → creates chapter 01-fundamentals/

6. fresh learn add probability-theory/01/... --content "..."

7. fresh learn concept complete probability-theory/fundamentals
   → next suggestion: distributions or conditional
```

## Integration with Backlog

The queue and backlog work together:

```bash
# View backlog (all discovered)
fresh learn backlog probability-theory

# Add to queue (what to learn next)
fresh learn concept add probability-theory gaussian

# See queue (what to learn)
fresh learn concept queue probability-theory

# Get next
fresh learn concept next probability-theory
```

## Options

### Priority Levels

| Priority | When to Use | Queue Position |
|----------|--------------|----------------|
| **high** | Core concepts, prerequisites | Top |
| **medium** | Standard concepts | Middle |
| **low** | Nice-to-have, advanced | Bottom |

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | In queue, not started |
| `in_progress` | Currently learning |
| `completed` | Finished |
| `skipped` | Skipped (for now) |

## Examples

### Complete Workflow

```bash
# 1. Discover concepts
fresh learn explore probability
# → fundamentals, conditional, distributions

# 2. Add to queue
fresh learn concept add probability-theory fundamentals --priority high
fresh learn concept add probability-theory conditional --priority medium
fresh learn concept add probability-theory distributions --priority medium

# 3. Start first
fresh learn concept next probability-theory
# → fundamentals
fresh learn concept start probability-theory/fundamentals

# 4. Create content
fresh learn chapter probability-theory 01-fundamentals
fresh learn add probability-theory/01/01-sample-space --content "..."

# 5. Complete
fresh learn concept complete probability-theory/fundamentals

# 6. Next
fresh learn concept next probability-theory
# → conditional (next highest priority)
```
