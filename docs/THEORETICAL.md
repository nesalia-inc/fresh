# Theoretical Learning

> How Fresh handles non-technical topics using Learn Mode.

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

## Solution: Learn Mode

For theoretical topics, use **Learn Mode** - the iterative learning system.

```
.fresh/
└── learning/                    # Learn Mode
    └── probability-theory/
        ├── 01-fundamentals/
        │   ├── 01-sample-space.md
        │   ├── 02-events.md
        │   └── 03-probability-function.md
        ├── 02-conditional/
        └── 03-distributions/
```

## Workflow

### Step 1: Initialize

```bash
fresh learn init probability-theory
```

### Step 2: Explore

```bash
fresh learn explore probability
# Returns: [fundamentals, distributions, statistics, bayes, random-variables]
```

### Step 3: Structure

```bash
fresh learn chapter probability-theory 01-fundamentals
fresh learn chapter probability-theory 02-distributions
fresh learn chapter probability-theory 03-bayes
```

### Step 4: Add Content (Iterative)

```bash
# Use web search to find content
fresh websearch "sample space probability theory"

# Add to learning project
fresh learn add probability-theory/01-fundamentals/01-sample-space \
  --content "# Sample Space

## Definition
The set of all possible outcomes of an experiment.

## Examples
- Coin flip: Ω = {H, T}
- Dice roll: Ω = {1, 2, 3, 4, 5, 6}
"
```

### Step 5: Link Concepts

```bash
fresh learn link \
  probability-theory/01-fundamentals/01-sample-space \
  probability-theory/02-conditional/independence
```

### Step 6: Iterate

```bash
# Discover more sub-concepts
fresh learn explore "conditional probability"
# Returns: [bayes-theorem, independence, chain-rule]

# Add more content...
```

## Comparison with Technical Topics

| Aspect | Technical | Theoretical |
|--------|-----------|-------------|
| **Source** | Official docs | Web search + synthesis |
| **Sync** | `fresh sync <topic>` | `fresh learn init` |
| **Content** | Auto-fetched | Agent adds manually |
| **Structure** | From doc site | Agent creates |

## Example: Building a Learning Project

```bash
# 1. Initialize
fresh learn init linear-algebra

# 2. Explore main topics
fresh learn explore "linear algebra"
# → [vectors, matrices, determinants, eigenvalues, linear-transformations]

# 3. Create structure
fresh learn chapter linear-algebra 01-vectors
fresh learn chapter linear-algebra 02-matrices
fresh learn chapter linear-algebra 03-eigenvalues

# 4. Add content iteratively
fresh websearch "what is a vector linear algebra"
fresh learn add linear-algebra/01-vectors/01-definition --content "..."

fresh websearch "vector operations addition scalar"
fresh learn add linear-algebra/01-vectors/02-operations --content "..."

# 5. Link concepts
fresh learn link linear-algebra/01-vectors/02-operations -> linear-algebra/02-matrices/01-matrix-multiplication

# 6. Continue until complete
```

## Why This Works

1. **Iterative** - Agent discovers concepts gradually
2. **Structured** - Hierarchical chapters/sections
3. **Linked** - Concepts connect to each other
4. **Agent-controlled** - Agent decides depth and order

## Tips

- Start with `fresh learn explore <topic>` to discover sub-topics
- Use web search (`fresh websearch`) to find content
- Add content incrementally
- Link related concepts with `fresh learn link`
- Use `fresh learn tree <project>` to see progress
