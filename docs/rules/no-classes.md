# No Classes Rule

**Rule ID:** `no-classes`

**Enforced:** Yes

## Principle

Prefer functional patterns over class-based design. Use factory functions and plain objects instead of classes.

## Rationale

- **Simplicity**: Functions are easier to reason about, test, and compose
- **Immutability**: Factory functions naturally encourage immutable patterns
- **Tree-shaking**: Individual exports are easier for bundlers to optimize
- **TypeScript**: Interface-based designs pair better with functional approaches

## Pattern

Instead of:

```typescript
// ❌ Class-based
class FreshClient {
  constructor(apiKey: string) { ... }
  search(options: SearchOptions): Promise<SearchResult> { ... }
  fetch(urls: string[], options?: FetchOptions): Promise<FetchResult> { ... }
}

const fresh = new FreshClient(apiKey);
```

Use:

```typescript
// ✅ Function-based
interface FreshInstance {
  search: (options: SearchOptions) => Promise<SearchResult>;
  fetch: (urls: string[], options?: FetchOptions) => Promise<FetchResult>;
}

function createFresh(apiKey: string): FreshInstance {
  return {
    search: async (options) => { ... },
    fetch: async (urls, options) => { ... },
  };
}

const fresh = createFresh(apiKey);
```

## Enforcement

- ESLint rule: `@typescript-eslint/no-explicit-any` (encourage explicit types)
- Code review: Reject class-based patterns in PRs
- Architecture reviews: Functional patterns are the default

## Exceptions

Framework integration patterns that inherently require classes (React components, Next.js route handlers) are exempt from this rule.

## Related Rules

- [deesse-fp pipe-flow](../../../.claude/skills/deesse-fp/rules/pipe-flow.md) - Function composition patterns
- [deesse-fp try rules](../../../.claude/skills/deesse-fp/rules/try.md) - Wrapping throwing functions
- [deesse-fp error handling](../../../.claude/skills/deesse-fp/rules/error-handling.md) - Error patterns
