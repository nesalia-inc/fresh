# Fresh Agent (Optional)

> The Agent is an **optional** enhancement. CLI handles most cases. Agent only for complex synthesis.

## Philosophy

**CLI first, Agent when necessary.**

Most operations should be done via CLI:
- Fetching documentation → CLI (`fresh sync`)
- Searching → CLI (`fresh search`)
- Basic guide creation → CLI (`fresh guide create`)

The Agent is only needed for:
- Complex synthesis across multiple sources
- Advanced analysis that requires reasoning
- Generating guide structure from scratch

## When to Use Agent

### CLI Can Do

```bash
# Fetch docs
fresh sync zod

# Search
fresh search "email validation" zod

# Simple guide
fresh guide create zod-basics --content "# Zod Basics\n\n..."
```

### Agent Needed

```python
from fresh import FreshAgent

agent = FreshAgent()

# Synthesis across multiple topics
guide = agent.learn(
    topic="optimistic-state-management",
    sources=["react", "tanstack-query", "zustand"],
    focus="best-practices"
)

# Complex migration guide
migration = agent.compare("zod", "v3", "v4")

# Generate guide structure
structure = agent.synthesize(
    query="how to handle forms in React",
    sources=["react", "react-hook-form", "zod"]
)
```

## Decision Flow

```
User Request
     │
     ▼
Can CLI handle this?
     │
     ├── YES → Use CLI
     │
     └── NO → Use Agent
           ├── Need multi-source synthesis?
           ├── Need complex comparison?
           ├── Need advanced reasoning?
           └── YES → Agent
```

## Agent Capabilities

### Synthesis

Combine information from multiple sources:

```python
guide = agent.synthesize(
    query="optimistic updates",
    sources=["react", "tanstack-query", "zustand"]
)
# → Guide combining best practices from all 3 sources
```

### Comparison

Compare versions:

```python
diff = agent.compare("zod", "v3", "v4")
# → Migration guide: what changed, how to upgrade
```

### Structure Generation

Create guide skeleton:

```python
structure = agent.structure(
    topic="authentication",
    sources=["nextjs", "nextauth"]
)
# → Guide outline with sections to fill
```

## Invocation

### Explicit

User explicitly requests agent:

```bash
fresh learn "topic" --agent
# or
fresh compare zod v3 v4 --agent
```

### Programmatic

```python
from fresh import FreshAgent

agent = FreshAgent()
result = agent.learn(...)
```

## Not a Replacement

The Agent is **not** a replacement for CLI:

- CLI is fast, reliable, deterministic
- Agent is slow (LLM calls), may vary

**Rule:** If you can do it with CLI, do it with CLI.
