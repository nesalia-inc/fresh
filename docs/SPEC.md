# Fresh V2 - Agent Knowledge System Specification

## Overview

Fresh V2 has **two distinct modes** for two different use cases:

1. **Run Mode** - Daily usage: retrieve information, quick references
2. **Learn Mode** - Knowledge creation: build structured learning projects

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRESH                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────┐     ┌─────────────────────┐       │
│   │   RUN MODE          │     │   LEARN MODE         │       │
│   │   (Usage quotidien) │     │   (Création formation)      │
│   └─────────────────────┘     └─────────────────────┘       │
│            │                            │                       │
│            ▼                            ▼                       │
│   • Consulter guides          • Créer learning projects        │
│   • Rechercher dans doc       • Explorer concepts             │
│   • Référence rapide          • Construire structure          │
│                                  Itérative discovery            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Run Mode (Utilisation Quotidienne)

Used when the agent **already has knowledge** and needs to retrieve it quickly.

### Use Cases

- Agent needs to remember something while coding
- Quick reference lookup
- Search across known topics
- Read a specific guide

### Commands

```bash
# Search in local docs
fresh search "email validation"
fresh search "zustand store" zustand

# View guides
fresh guide list
fresh guide show optimistic-state

# Check knowledge
fresh knowledge list
fresh knowledge status zod

# Quick guide creation (personal notes)
fresh guide create my-reference --content "..."
```

### Output

Quick answers, references, not creation of new knowledge.

---

## Learn Mode (Création de Formation)

Used when the agent **builds its knowledge** - iterative, structured process.

### Use Cases

- Agent wants to learn a new topic (technical or theoretical)
- Building comprehensive knowledge base
- Creating structured learning materials

### The Learning Process

```
1. fresh learn init <topic>
   → Create learning project

2. fresh learn explore <topic>
   → Discover sub-topics

3. [Iteration loop]
   a. fresh learn chapter <project>/<chapter>
   b. fresh learn add <path> --from-search "..."
   c. fresh learn link <path1> <path2>
   d. Discover new sub-concepts → repeat

4. → .fresh/learning/<topic>/ (structured book)
```

### Commands

```bash
# Project management
fresh learn init <name>              # Create learning project
fresh learn list                     # List all learning projects
fresh learn tree <project>           # Show structure
fresh learn delete <project>         # Delete project

# Exploration
fresh learn explore <topic>          # Discover sub-topics
fresh learn suggestions <project>    # What's next

# Structure
fresh learn chapter <project>/<chapter>   # Create chapter
fresh learn section <project>/<chapter>/<section>  # Create section

# Content
fresh learn add <path> --content "..."           # Add content
fresh learn add <path> --from-search "..."      # Add from web search
fresh learn edit <path>                          # Edit content

# Navigation
fresh learn show <path>              # Show content
fresh learn find <project> <query>  # Search in project

# Linking
fresh learn link <path1> <path2>    # Link concepts
fresh learn graph <project>          # Show knowledge graph

# Progress
fresh learn status <project>         # Show progress
fresh learn next <project>          # Suggest next step
```

---

## Project Structure

```
.fresh/
├── knowledge/                       # RUN MODE: Synced technical docs
│   ├── zod/
│   │   └── docs/
│   └── react/
│       └── docs/
│
├── guides/                         # RUN MODE: Quick reference guides
│   ├── optimistic-state.md
│   └── forms-with-zod.md
│
└── learning/                       # LEARN MODE: Learning projects
    ├── probability-theory/
    │   ├── _meta/
    │   │   ├── index.json         # Concepts index
    │   │   ├── graph.json         # Links between concepts
    │   │   └── progress.json      # Progress tracking
    │   ├── 01-fundamentals/
    │   │   ├── _meta.yaml
    │   │   ├── 01-sample-space.md
    │   │   ├── 02-events.md
    │   │   └── 03-probability-function.md
    │   ├── 02-conditional/
    │   └── 03-distributions/
    └── linear-algebra/
        └── ...
```

---

## Example: Learn Mode Workflow

### Step 1: Initialize

```bash
fresh learn init probability-theory
# Creates .fresh/learning/probability-theory/
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
# Search for a concept
fresh websearch "sample space probability"

# Add to learning project
fresh learn add probability-theory/01-fundamentals/01-sample-space \
  --content "# Sample Space

## Definition
The set of all possible outcomes of an experiment.

## Example
Coin flip: Ω = {H, T}
Dice roll: Ω = {1, 2, 3, 4, 5, 6}

## Notation
Ω (Omega)
"
```

### Step 5: Link Concepts

```bash
fresh learn link \
  probability-theory/01-fundamentals/01-sample-space \
  probability-theory/02-conditional/independence
# → Creates dependency link in graph
```

### Step 6: Iterate

```bash
# Discover new sub-concepts
fresh learn explore "conditional probability"
# → Returns: [bayes-theorem, independence, chain-rule]

# Continue adding...
```

---

## Theoretical Learning

Learn Mode handles both technical AND theoretical topics:

### Technical (has doc sites)

```bash
fresh learn init react-patterns

# Can also sync docs
fresh sync react

# Then add from local docs
fresh learn add react-patterns/hooks --from-search "useEffect cleanup"
```

### Theoretical (no doc sites)

```bash
fresh learn init probability-theory

# Use web search to discover and add
fresh websearch "probability theory fundamentals"
fresh learn add probability-theory/... --content "..."

# Iterate until complete
```

---

## Comparison

| Aspect | Run Mode | Learn Mode |
|--------|----------|------------|
| **When** | Daily, while coding | Before/alongside coding |
| **Purpose** | Retrieve info | Create knowledge |
| **Output** | Quick references | Structured book |
| **Iteration** | No | Yes (discovery loop) |
| **Commands** | `search`, `guide show` | `learn init`, `explore`, `add` |
| **Structure** | Flat guides | Hierarchical chapters |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                               │
│   Run: sync │ search │ guide │ knowledge                  │
│   Learn: learn init │ explore │ chapter │ add │ link      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Scraping   │  │   Search     │  │   Learning   │   │
│  │   Service    │  │   Service    │  │   Service    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Storage (.fresh/)                          │
│   knowledge/ (docs) │ guides/ (quick refs) │ learning/     │
│          SQLite (index) + Markdown (content)               │
└─────────────────────────────────────────────────────────────┘
```

---

## Roadmap

### Phase 1 (Run Mode - Current)
- [x] CLI commands
- [x] Guide management
- [ ] Project-local `.fresh/` directory
- [ ] SQLite search index

### Phase 2 (Learn Mode)
- [ ] `fresh learn init` - Learning project creation
- [ ] `fresh learn explore` - Concept discovery
- [ ] `fresh learn chapter/section` - Structure
- [ ] `fresh learn add` - Content addition
- [ ] `fresh learn link` - Knowledge graph
- [ ] Iteration support

### Phase 3 (Advanced)
- [ ] Progress tracking
- [ ] Suggestions engine
- [ ] Agent automation
- [ ] MCP server
