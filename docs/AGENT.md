# Fresh is a CLI

Fresh is a CLI tool. Both humans and AI agents use the same commands.

There's no special "Agent Mode" - just a CLI that anyone can use.

## For AI Agents

An AI agent can use Fresh like any other CLI tool:

```bash
# Agent fetches docs
fresh sync zod
fresh sync react

# Agent searches
fresh search "email validation" zod

# Agent learns
fresh learn init state-management
fresh learn explore "state management"
fresh learn add state-management fundamentals --priority high
fresh learn next
```

## For Humans

Humans use the same commands:

```bash
fresh sync python
fresh learn init probability-theory
fresh learn explore probability
fresh learn queue
```

## No Difference

The CLI is the interface. Who calls it doesn't matter.
