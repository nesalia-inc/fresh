# Unified Learning Theory

> Every technical tool is an implementation of a theoretical concept.

## The Insight

Technical frameworks/libraries are just **implementations of theoretical concepts**:

| Theory | Implementations |
|--------|-----------------|
| Client State Management | Zustand, Redux, TanStack Query |
| Schema Validation | Zod, Yup, Joi |
| Reactive UI | React, Vue, Svelte |
| HTTP Caching | TanStack Query, SWR |
| Form Validation | React Hook Form, Formik |
| Routing | React Router, Next.js, Vue Router |
| Testing | Jest, Vitest, Playwright |

**Learning the theory first makes learning implementations easier.**

## Unified Concept System

All learning projects are the same - they just have different sources:

```
fresh learn init state-management
fresh learn init zustand
```

Both are concepts. The difference:
- `state-management` → theoretical (no official docs)
- `zustand` → technical (has official docs)

## Technical vs Theoretical

### Technical Concepts

Have official documentation:
```bash
fresh sync zod              # Fetch docs
fresh learn init zustand    # Create project
fresh sync zustand          # Fetch docs
```

### Theoretical Concepts

No official docs, build from web search:
```bash
fresh learn init state-management
fresh learn explore "client state management"
```

### They Connect

When learning a technical tool, link it to the theory:

```bash
# Learn Zustand
fresh learn concept add my-project zustand --from state-management

# Link to theory
fresh learn link my-project/zustand → my-project/state-management
```

## Learning Flow

### 1. Identify the Problem

```
Agent: "I need to handle server state"
→ Problem: "server state management"
```

### 2. Learn the Theory

```bash
fresh learn init server-state-management
fresh learn concept add server-state-management fundamentals --priority high
fresh learn concept add server-state-management caching --priority high
fresh learn concept add server-state-management invalidation --priority medium
# ... learn the theory
```

### 3. Learn Implementations

```bash
# Now learn how to implement
fresh learn init tanstack-query
fresh learn sync tanstack-query

fresh learn init swr
fresh learn sync swr
```

### 4. Connect

```bash
# Link implementations to theory
fresh learn link tanstack-query → server-state-management
fresh learn link swr → server-state-management
```

## Example: State Management

### Step 1: Learn the Theory

```bash
fresh learn init state-management
fresh learn concept add state-management fundamentals --priority high
fresh learn concept add state-management client-vs-server --priority high
fresh learn concept add state-management optimistic-updates --priority medium
```

### Step 2: Learn Implementations

```bash
# Learn each implementation
fresh learn init zustand
fresh learn sync zustand

fresh learn init tanstack-query
fresh learn sync tanstack-query

fresh learn init redux
fresh learn sync redux
```

### Step 3: Connect

```bash
# Link implementations to theory
fresh learn link zustand → state-management
fresh learn link tanstack-query → state-management
fresh learn link redux → state-management
```

## Benefits

1. **Understand WHY** - Not just how to use Zustand, but why you'd use it
2. **Transfer knowledge** - Learn Zustand → easy to learn Redux
3. **Choose wisely** - Understand tradeoffs between implementations
4. **Build intuition** - Theory applies everywhere

## Structure

```
.fresh/learning/
├── state-management/           # Theory
│   ├── 01-fundamentals/
│   ├── 02-client-vs-server/
│   └── 03-patterns/
│
├── zustand/                   # Implementation
│   └── docs/
│
├── tanstack-query/            # Implementation
│   └── docs/
│
└── redux/                     # Implementation
    └── docs/
```

## Commands for Connections

```bash
# Link implementation to theory
fresh learn link zustand state-management

# View connections
fresh learn graph zustand

# Find related concepts
fresh learn related zustand
# → Returns: [state-management, redux, tanstack-query]
```

## The Learning Path

```
Problem → Theory → Implementations

1. "I need to handle server state"
   ↓
2. Learn theory: "server state management"
   ↓
3. Learn implementations: TanStack Query, SWR
   ↓
4. Choose based on needs
```

This is how experts think - they understand the theory, then learn the tools that implement it.
