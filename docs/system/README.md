# System Documentation

Comprehensive documentation on building AI agents that produce quality software through training, verification, and automated systems.

## Overview

This system addresses three fundamental challenges in agent-based software development:

1. **Knowledge** - Agents must have access to up-to-date information (see [Agent Knowledge System](../agent-knowledge-system.md))
2. **Quality** - Agents must produce high-quality code (see [Quality](./quality/))
3. **Verification** - Code must be verified at multiple levels (see [Verification](./verification/))

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                 TRAINING LAYER                          │  │
│   │                                                         │  │
│   │   - Foundation rules (always follow)                   │  │
│   │   - Pattern library (usually follow)                   │  │
│   │   - Context awareness (decide when)                   │  │
│   │                                                         │  │
│   │   See: [Training](./training/)                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              VERIFICATION LAYER                         │  │
│   │                                                         │  │
│   │   - Syntax gates (ESLint)                             │  │
│   │   - Type gates (TypeScript)                           │  │
│   │   - Test gates (Vitest)                               │  │
│   │   - Security gates (AI-powered)                       │  │
│   │   - Quality gates (AST-based)                         │  │
│   │   - Agent verification                                  │  │
│   │                                                         │  │
│   │   See: [Verification](./verification/)                │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │               AUTOMATION LAYER                           │  │
│   │                                                         │  │
│   │   - Algorithm selection                                │  │
│   │   - Performance optimization                           │  │
│   │   - Security scanning                                  │  │
│   │   - Framework primitives                               │  │
│   │                                                         │  │
│   │   See: [Automation](./automation/)                     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Zero Trust Knowledge

Agents must never trust their training data. All knowledge must come from external sources with explicit freshness indicators.

See: [Agent Knowledge System](../agent-knowledge-system.md)

### 2. Quality Rules

Code quality goes beyond linting and types. Agents need:
- Error handling rules
- Function quality rules
- Testing quality rules
- Architecture rules
- Security rules

See: [Quality Rules](./quality/rules/rules.md)

### 3. Gates as Portals

Verification tools should be gates that block if requirements aren't met, not just warnings.

See: [Verification Gates](./verification/gates.md)

### 4. Framework Primitives

Common building blocks (auth, permissions, caching, etc.) should be primitives with built-in gates.

See: [Framework Primitives](./patterns/framework-primitives.md)

## Directory Structure

```
docs/system/
├── README.md                 # This file
├── training/
│   └── index.md             # Agent training methodology
├── verification/
│   └── gates.md             # Gate-based verification system
├── quality/
│   ├── overview.md          # Code quality system overview
│   └── rules/
│       ├── README.md
│       └── rules.md         # Detailed quality rules
├── patterns/
│   ├── extraction.md        # Pattern extraction process
│   ├── building-blocks.md  # Common building blocks
│   ├── determinism.md      # Reducing mental load
│   └── framework-primitives.md
└── automation/
    ├── algorithm-performance.md
    └── security.md
```

## Related Documents

- [Agent Knowledge System](../agent-knowledge-system.md) - Knowledge freshness
- [Guide Workflow](../workflow/guides.md) - Using fresh for documentation

---

*Last updated: 2026-03-04*
