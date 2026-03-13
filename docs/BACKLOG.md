# Concept Backlog

> How Fresh stores discovered concepts for future iterations.

## The Problem

When learning, the agent discovers new concepts continuously:

```
1. Agent explores "probability"
   → Finds: [fundamentals, conditional, distributions]

2. Agent explores "distributions"
   → Discovers: [gaussian, binomial, poisson, etc.]

3. These new concepts need to be saved for later!
```

## Solution: Concept Backlog

A backlog stores all discovered concepts, organized by iteration and priority.

```
.fresh/learning/probability-theory/
├── _meta/
│   ├── backlog.json        # All discovered concepts
│   ├── progress.json       # Current state
│   └── graph.json          # Concept links
├── 01-fundamentals/
├── 02-conditional/
└── 03-distributions/
```

## Backlog Structure

```json
// .fresh/learning/probability-theory/_meta/backlog.json
{
  "project": "probability-theory",
  "discovered": [
    {
      "id": "gaussian-distribution",
      "name": "Gaussian Distribution",
      "discovered_at": "2026-03-13T10:00:00Z",
      "discovered_from": "distributions",
      "status": "pending",
      "priority": "medium"
    },
    {
      "id": "binomial-distribution",
      "name": "Binomial Distribution",
      "discovered_at": "2026-03-13T10:00:00Z",
      "discovered_from": "distributions",
      "status": "pending",
      "priority": "medium"
    },
    {
      "id": "central-limit-theorem",
      "name": "Central Limit Theorem",
      "discovered_at": "2026-03-13T10:01:00Z",
      "discovered_from": "gaussian",
      "status": "pending",
      "priority": "high"
    }
  ],
  "exploring": "conditional",
  "completed": ["fundamentals"]
}
```

## Iteration Workflow

### Iteration 1: Initial Discovery

```bash
# Explore main topic
fresh learn explore probability

# Returns:
# - fundamentals (suggested first)
# - conditional (depth 2)
# - distributions (depth 2)

# Save to backlog (automatic)
# backlog now has: [conditional, distributions]
```

### Iteration 2: First Learning

```bash
# Start with fundamentals
fresh learn chapter probability-theory 01-fundamentals
fresh learn add probability-theory/01/... --content "..."

# Complete fundamentals
# Status: completed: [fundamentals]
```

### Iteration 3: Discover More

```bash
# Explore a learned topic → discovers new concepts
fresh learn explore probability-theory/distributions

# Discovers: [gaussian, binomial, poisson]
# Adds to backlog

# Backlog now has: [conditional, gaussian, binomial, poisson]
```

### Iteration 4: Continue Learning

```bash
# See what's next
fresh learn next probability-theory

# Returns: "Next: learn 'conditional' (from backlog)"

# Learn conditional
fresh learn chapter probability-theory 02-conditional
```

### Iteration 5: Deep Dive

```bash
# Explore what you just learned
fresh learn explore probability-theory/conditional

# Discovers new concepts
# Adds to backlog

# Explore the new concepts
fresh learn explore probability-theory/gaussian
```

## Commands

### View Backlog

```bash
fresh learn backlog probability-theory
```

Output:
```
📚 Probability Theory - Backlog

Completed: fundamentals
Exploring: conditional

Discovered concepts:
- gaussian (from: distributions) [medium priority]
- binomial (from: distributions) [medium priority]
- poisson (from: distributions) [medium priority]

Next: conditional
```

### Add to Backlog

```bash
# Manual add
fresh learn add-to-backlog probability-theory \
  --concept "markov-chains" \
  --from "stochastic-processes"
```

### Mark as Learning

```bash
fresh learn start probability-theory/gaussian
# Sets exploring: gaussian
```

### Mark as Complete

```bash
fresh learn complete probability-theory/fundamentals
# Moves from exploring/discovered to completed
```

### Get Next Suggestion

```bash
fresh learn next probability-theory
# Returns: "conditional" (based on prerequisites and order)
```

## Priority System

Concepts can have priorities:

| Priority | When | Example |
|----------|------|---------|
| **high** | Core concepts needed for advanced topics | CLT for statistics |
| **medium** | Standard concepts | Most distributions |
| **low** | Nice-to-have, advanced | Edge cases |

```bash
# Auto-detected priority
fresh learn explore probability-theory/distributions
# - gaussian → high (prerequisite for CLT)
# - binomial → medium

# Manual override
fresh learn priority probability-theory/markov-chains --high
```

## Prerequisites Tracking

```json
// Concept with prerequisites
{
  "id": "central-limit-theorem",
  "prerequisites": ["gaussian", "normal-distribution"],
  "can_start": false,
  "blocking": ["gaussian"]
}
```

## Visual Progress

```bash
fresh learn progress probability-theory
```

```
probability-theory
├── ✅ Fundamentals (complete)
│   ├── ✅ Sample Space
│   ├── ✅ Events
│   └── ✅ Probability Function
├── 🔄 Conditional (in progress)
│   ├── ✅ Definition
│   └── ⏳ Bayes Theorem
└── ⏳ Distributions (backlog)
    ├── gaussian (priority: high)
    ├── binomial (priority: medium)
    └── poisson (priority: medium)

Backlog:
- central-limit-theorem (priority: high, needs: gaussian)
- markov-chains (priority: low)
```

## Why This Matters

1. **Never forget** - All discovered concepts are saved
2. **Iterative** - Learn simple first, complex later
3. **Prioritized** - Know what matters most
4. **Trackable** - See progress and what's next
