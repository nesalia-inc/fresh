# Theoretical Learning

> How Fresh handles non-technical topics like mathematics, statistics, and theory.

## The Problem

Fresh handles technical documentation well:
- `fresh sync zod` → get Zod docs locally
- Search, create guides, etc.

But what about **theoretical topics**?
- Probability & Statistics
- Linear Algebra
- Algorithm Theory
- Machine Learning Fundamentals
- etc.

These have no "doc site" to sync. Traditional scraping doesn't work.

## The Distinction

| Type | Example | Approach |
|------|---------|----------|
| Technical | Zod, React, Python | Sync docs from official sites |
| Theoretical | Proba/stats, Algebra | Different approach needed |

## Solutions

### Solution 1: Web Search + Agent Synthesis (Recommended)

Use existing `fresh websearch` and let the agent iterate:

```
Agent wants to learn "probability theory"

1. fresh websearch "probability theory fundamentals"
   → Returns web results

2. Agent reads results, understands concepts

3. fresh guide create probability-theory
   → Creates empty guide

4. fresh guide add probability-theory --content "# Fundamentals\n\n..."
   → Adds synthesized content

5. Repeat 1-4 until guide is complete
```

**Pros:**
- Uses existing tools (`fresh websearch` already exists)
- Agent controls depth and synthesis
- No new infrastructure needed

**Cons:**
- Manual iteration required
- Agent does more work

### Solution 2: Curated Sources

Define trusted sources for theoretical topics:

```python
# In config or as built-in
THEORETICAL_SOURCES = {
    "probability": [
        "https://en.wikipedia.org/wiki/Probability",
        "https://mathworld.wolfram.com/Probability",
    ],
    "statistics": [
        "https://en.wikipedia.org/wiki/Statistics",
        "https://mathworld.wolfram.com/Statistics",
    ],
    "linear-algebra": [
        "https://en.wikipedia.org/wiki/Linear_algebra",
        "https://mathworld.wolfram.com/LinearAlgebra",
    ],
    "machine-learning": [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://machinelearningmastery.com/",
    ],
}
```

Then:
```bash
fresh sync probability
→ Fetches from curated sources
→ Same workflow as technical docs
```

**Pros:**
- Automatic
- Consistent with existing workflow

**Cons:**
- Need to maintain source list
- Wikipedia may not be the best source
- May need web scraping anyway

### Solution 3: Agent Full Automation

The Agent handles everything:

```python
from fresh import FreshAgent

agent = FreshAgent()

# Agent searches, synthesizes, creates guide
guide = agent.learn(
    topic="probability-theory",
    mode="theoretical",  # Different from technical
    depth="comprehensive"
)
```

Agent would:
1. Search web for relevant information
2. Analyze and synthesize
3. Create structured guide
4. Return complete guide

**Pros:**
- "Magical" experience
- Agent does all the work

**Cons:**
- Most complex to implement
- Less control
- Requires LLM integration

## Recommended Approach

### Phase 1: Use Existing Tools (Now)

```bash
# Agent uses web search to learn
fresh websearch "probability theory fundamentals"

# Agent creates guide
fresh guide create probability-theory

# Agent enriches guide iteratively
fresh guide add probability-theory --content "..."
fresh guide add probability-theory --content "..."
```

The agent iterates until it has a comprehensive guide.

### Phase 2: Curated Sources (Later)

Add built-in sources for common theoretical topics:
- math.stackexchange
- wikipedia (carefully selected pages)
- university course notes

```bash
fresh sync probability
# → Fetches from predefined sources
```

### Phase 3: Agent Automation (Future)

When Agent mode is ready:
```bash
fresh learn "probability theory" --agent
# → Fully automated synthesis
```

## Example Workflow

### Agent Learning Probability

```bash
# 1. Agent decides it needs probability theory
#    (maybe because project involves statistics)

# 2. Start with web search
fresh websearch "probability theory basics"

# 3. Create guide
fresh guide create probability-fundamentals

# 4. Agent synthesizes and adds content
fresh guide add probability-fundamentals \
  --content "# Probability Fundamentals

## Core Concepts

### Sample Space (Ω)
The set of all possible outcomes...

### Events
A subset of the sample space...

### Probability Function
P: Ω → [0,1]

## Key Theorems

### Bayes' Theorem
P(A|B) = P(B|A) * P(A) / P(B)

..."

# 5. Search for more specific topics
fresh websearch "conditional probability examples"

# 6. Add more content
fresh guide add probability-fundamentals \
  --content "## Conditional Probability

### Definition
P(A|B) = P(A ∩ B) / P(B)

### Example
..."

# 7. Continue until comprehensive
fresh guide show probability-fundamentals
```

## Comparison

| Solution | Complexity | Control | Automation |
|----------|------------|---------|------------|
| Web search + manual | Low | High | Low |
| Curated sources | Medium | Medium | Medium |
| Agent full | High | Low | High |

## Decision

Start with **Solution 1** (web search + manual) because:
1. Uses existing `fresh websearch` command
2. Agent has full control over what to learn
3. No new infrastructure needed
4. Can evolve to other solutions later

The agent becomes the "curator" - it decides what to search, what to keep, and how to synthesize.
