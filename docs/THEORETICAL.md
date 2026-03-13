# Learning Theoretical Topics

Fresh handles theoretical topics (no official docs) with the same learning system.

## Workflow

```bash
# 1. Start
fresh learn init probability-theory

# 2. Explore
fresh learn explore probability
# → Returns: [fundamentals, distributions, conditional]

# 3. Add to queue
fresh learn add probability-theory fundamentals --priority high
fresh learn add probability-theory distributions --priority medium

# 4. Learn
fresh learn next
fresh learn start fundamentals
fresh learn add probability-theory/01-sample-space --content "..."
fresh learn done fundamentals

# 5. Explore deeper → discover new concepts
fresh learn explore probability/distributions

# 6. Add discoveries to queue
fresh learn add probability-theory gaussian --priority high

# 7. Repeat
```

## Priority

- **high**: Core concepts, prerequisites
- **medium**: Standard concepts
- **low**: Nice-to-have

## Commands

| Command | Description |
|---------|-------------|
| `fresh learn init <topic>` | Create project |
| `fresh learn explore <topic>` | Discover concepts |
| `fresh learn add <concept> --priority high|medium|low` | Add to queue |
| `fresh learn queue` | View queue |
| `fresh learn next` | Get next concept |
| `fresh learn start <concept>` | Start learning |
| `fresh learn done <concept>` | Mark complete |
