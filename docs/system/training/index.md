# Training System

How to train agents to produce quality code.

## Core Philosophy

Agents need three layers of training:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THREE-LAYER TRAINING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   LAYER 1: Foundation Rules                                     │
│   ━━━━━━━━━━━━━━━━━━━━━                                         │
│   - Never use "any" in TypeScript                               │
│   - Always handle errors                                        │
│   - Never commit secrets                                        │
│   - Max function length: 30 lines                               │
│   → Agent MUST follow these always                               │
│                                                                 │
│   LAYER 2: Pattern Library                                      │
│   ━━━━━━━━━━━━━━━━━━                                           │
│   - Show 1000s of good examples                                 │
│   - Agent learns patterns                                        │
│   - Can adapt to context                                        │
│   → Agent USUALLY follows these                                 │
│                                                                 │
│   LAYER 3: Context Awareness                                   │
│   ━━━━━━━━━━━━━━━━━━━━━                                         │
│   - This is an Enterprise project → stricter rules            │
│   - This is a MVP → faster, less testing                       │
│   - This is a library → extensive docs                          │
│   → Agent DECIDES based on context                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## The Impossible Package

The challenge of making quality mandatory through library design:

```
Goal: Using the package CORRECTLY = Writing QUALITY code

Why it's hard:
- Attempt 1: Typed errors → Agent can ignore Result
- Attempt 2: Result pattern → Agent can do if (!ok) return;
- Attempt 3: Railway-oriented → Too complex, agent skips

Real Solution: Multiple approaches COMBINED
- Type system that forces handling
- ESLint rules that warn on misuse
- Runtime that logs ignored errors
- Documentation that explains WHY
```

See: [Train-Verify Document](./train-verify.md) for full details.

## Key Principles

1. **Don't theorize** - Take real code and analyze it
2. **Iterate** - Keep improving patterns
3. **Extract what's common** - Abstract the patterns
4. **Handle variations** - Support different contexts
5. **Design for evolution** - Make it easy to change

---

*Last updated: 2026-03-04*
