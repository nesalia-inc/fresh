# Code Quality System

A comprehensive system for ensuring agents produce high-quality code.

## The Problem: Knowledge ≠ Quality

```
Agent has up-to-date knowledge:
✓ Uses TanStack Query v5
✓ Uses TypeScript strict mode
✓ Uses modern React patterns

BUT produces mediocre code:
✗ No error handling visible to users
✗ Functions are 50+ lines long
✗ All tests are mocks
✗ No proper error boundaries
✗ Silent failures
```

## What Tools Don't Catch

| Tool | What it Catches | What it Misses |
|------|-----------------|----------------|
| ESLint | Syntax errors | Business logic quality |
| TypeScript | Type safety | Runtime behavior |
| Tests | Coverage % | Test quality |
| Prettier | Code style | Everything else |

## Quality Rule Categories

### 1. Error Handling (25%)
- No silent failures
- User-visible errors
- Loading states

### 2. Function Quality (25%)
- Max 30 lines per function
- Single responsibility
- Early returns
- No magic numbers

### 3. Testing Quality (20%)
- No all mocks
- Edge case tests
- Integration tests required

### 4. Architecture (15%)
- Separation of concerns
- Dependency injection

### 5. Security (15%)
- Input validation
- No sensitive data in logs

## Quality Score System

```
┌─────────────────────────────────────────────┐
│ QUALITY SCORE BREAKDOWN                     │
├─────────────────────────────────────────────┤
│                                             │
│ FUNCTIONAL CORRECTNESS (25%)                │
│ ├─ Tests pass (10%)                        │
│ ├─ TypeScript strict (10%)                 │
│ └─ No runtime errors (5%)                  │
│                                             │
│ ERROR HANDLING (25%)                        │
│ ├─ User-visible errors (10%)              │
│ ├─ Loading states (5%)                    │
│ └─ Empty states (5%)                     │
│                                             │
│ CODE STRUCTURE (25%)                       │
│ ├─ Function length (10%)                  │
│ ├─ Single responsibility (10%)             │
│ └─ No duplication (5%)                     │
│                                             │
│ TEST QUALITY (15%)                         │
│ ├─ Real tests (10%)                       │
│ └─ Edge cases (5%)                        │
│                                             │
│ SECURITY (10%)                             │
│ └─ No vulnerabilities (10%)               │
│                                             │
└─────────────────────────────────────────────┘
```

## Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | ✅ Excellent | Allow |
| 80-89 | ⚠️ Good | Allow with warnings |
| 70-79 | ❌ Needs Work | Block, show issues |
| <70 | ❌❌ Poor | Block + require rewrite |

## See Also

- [Detailed Quality Rules](./rules/rules.md)

---

*Last updated: 2026-03-04*
