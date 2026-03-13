# Theoretical Learning

> How Fresh handles non-technical topics using Learn Mode with concept queue.

## The Problem

Technical topics have official documentation sites:
- Zod → zod.dev
- React → react.dev
- Python → docs.python.org

But theoretical topics don't:
- Probability & Statistics
- Linear Algebra
- Algorithm Theory
- Machine Learning Fundamentals

## Solution: Learn Mode + Concept Queue

For theoretical topics, use **Learn Mode** with the **concept queue** - a priority-based learning system.

## The Workflow

### Step 1: Initialize

```bash
fresh learn init probability-theory
```

### Step 2: Explore & Add to Queue

```bash
fresh learn explore probability
# Returns: [fundamentals, distributions, conditional, random-variables]

# Add concepts to queue with priority
fresh learn concept add probability-theory fundamentals --priority high
fresh learn concept add probability-theory distributions --priority medium
fresh learn concept add probability-theory conditional --priority medium
```

### Step 3: Learn (Iterative)

```bash
# Get next concept
fresh learn concept next probability-theory
# → fundamentals (highest priority)

# Start learning
fresh learn concept start probability-theory/fundamentals

# Create content
fresh learn chapter probability-theory 01-fundamentals
fresh learn add probability-theory/01/01-sample-space --content "..."

# Complete
fresh learn concept complete probability-theory/fundamentals
```

### Step 4: Discover New Concepts

```bash
# Explore deeper → discovers new concepts
fresh learn explore probability/distributions

# Add discoveries to queue
fresh learn concept add probability-theory gaussian --priority high --from distributions
fresh learn concept add probability-theory binomial --priority medium --from distributions
fresh learn concept add probability-theory poisson --priority medium --from distributions
```

### Step 5: Continue

```bash
# View queue
fresh learn concept queue probability-theory
# Shows all concepts with priorities

# Next
fresh learn concept next probability-theory
# → gaussian (high priority, prerequisites met)
```

## Example: Building Probability Theory

```bash
# 1. Initialize
fresh learn init probability-theory

# 2. Explore main topics
fresh learn explore probability

# 3. Add to queue
fresh learn concept add probability-theory fundamentals --priority high
fresh learn concept add probability-theory conditional --priority medium
fresh learn concept add probability-theory distributions --priority medium
fresh learn concept add probability-theory random-variables --priority low

# 4. Learn fundamentals
fresh learn concept next probability-theory
# → fundamentals
fresh learn concept start probability-theory/fundamentals
fresh learn chapter probability-theory 01-fundamentals
fresh learn add probability-theory/01/01-sample-space --content "# Sample Space\n\n..."
fresh learn add probability-theory/01/02-events --content "# Events\n\n..."
fresh learn concept complete probability-theory/fundamentals

# 5. Explore → discover more
fresh learn explore probability/distributions

# 6. Add new concepts to queue
fresh learn concept add probability-theory gaussian --priority high --from distributions
fresh learn concept add probability-theory binomial --priority medium --from distributions

# 7. Learn next
fresh learn concept next probability-theory
# → gaussian (high priority)
fresh learn concept start probability-theory/gaussian

# 8. Continue iterating...
```

## Queue System

The concept queue manages what to learn next:

```bash
# View queue
fresh learn concept queue probability-theory
```
```
📚 probability-theory

Priority: high
├── [ ] gaussian (from: distributions)

Priority: medium
├── [ ] binomial (from: distributions)
├── [ ] conditional

Priority: low
└── [ ] random-variables

Completed: fundamentals
```

```bash
# Get next
fresh learn concept next probability-theory
# → gaussian (priority: high)
```

```bash
# Start/Complete
fresh learn concept start probability-theory/gaussian
fresh learn concept complete probability-theory/gaussian
```

## Why This Works

1. **Priority-based** - Most important concepts first
2. **Iterative** - Learn, discover, add, repeat
3. **Discovered concepts saved** - New concepts from exploration go to queue
4. **Trackable** - Always know what's next

## Commands Reference

| Command | Description |
|---------|-------------|
| `fresh learn init <topic>` | Initialize learning project |
| `fresh learn explore <topic>` | Discover concepts |
| `fresh learn concept add <project> <concept>` | Add to queue |
| `fresh learn concept queue <project>` | View queue |
| `fresh learn concept next <project>` | Get next concept |
| `fresh learn concept start <project>/<concept>` | Start learning |
| `fresh learn concept complete <project>/<concept>` | Mark complete |
| `fresh learn chapter <project>/<chapter>` | Create chapter |
| `fresh learn add <path> --content "..."` | Add content |
