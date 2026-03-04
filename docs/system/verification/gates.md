# Verification Gates

Verification tools should be gates that block if requirements aren't met.

## The Gate Metaphor

```
Think of verification tools as GATES:

CODE ──▶│ GATE │──▶│ GATE │──▶│ GATE │──▶ MERGE
        │ Qual │    │ Sec  │    │ Perf │
               │              │
               ▼              ▼
          ┌─────────────────────────────────┐
          │ IF GATE FAILS:                  │
          │ - BLOCK the PR                 │
          │ - SHOW what's wrong            │
          │ - SUGGEST fixes               │
          │ - PREVENT shipping bad code    │
          └─────────────────────────────────┘
```

## Claude Code Security Example

Claude Code Security is an AI-powered security gate:

- Scans code for security vulnerabilities
- Uses AI (not just pattern matching)
- Understands how components interact
- Multi-stage verification (Claude re-examines findings)
- Suggests PATCHES, not just problems
- Nothing applied without human approval

## React-Doctor Example

AST-based gate for React:

- Analyzes AST of React code
- Detects performance issues
- Detects correctness issues
- Runs as pre-commit or in CI

## Complete Gate System

```
CODE ──┬──▶ SYNTAX GATE (ESLint)
       ├──▶ TYPES GATE (TypeScript)
       ├──▶ TESTS GATE (Vitest)
       ├──▶ SECURITY GATE (Claude Code Security)
       ├──▶ QUALITY GATE (AST-based rules)
       ├──▶ PERFORMANCE GATE (Complexity analyzer)
       ├──▶ VERIFICATION AGENT (AI-powered review)
       └──▶ HUMAN REVIEW (final approval)

ANY GATE FAILURE = BLOCK
```

## Defense in Depth

| Layer | Type | What it Catches |
|-------|------|-----------------|
| 1 | Syntax | Trivial issues |
| 2 | Types | Type safety |
| 3 | Tests | Functionality |
| 4 | Security | AI-powered vulnerabilities |
| 5 | Quality | Patterns |
| 6 | Performance | Complexity |
| 7 | Agent | Comprehensive review |
| 8 | Human | Final check |

## Implementation

```
Option 1: pre-commit hooks
  .git/hooks/pre-commit:
    fresh-gate --staged

Option 2: CI/CD pipeline
  GitHub Actions:
    - run: fresh-gate --all
    - if: gates.fail
      then: block merge

Option 3: IDE integration
  VS Code extension:
    - Inline warnings
    - Quick fixes
    - Real-time feedback

Option 4: Dedicated verification agents
  In CI:
    - fresh-agent security
    - fresh-agent quality
    - fresh-agent performance
```

---

*Last updated: 2026-03-04*
