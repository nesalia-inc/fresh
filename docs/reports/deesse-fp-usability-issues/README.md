# Issue: Usability Problems with @deessejs/fp

## Summary

The `@deessejs/fp` library has significant usability issues that make it difficult to use correctly. The documentation does not match the actual API, and the API itself is unnecessarily complex with multiple similarly-named functions that handle the same operations for different types.

## Problem 1: Documentation Does Not Match Code

### Example from `try.md`

The documentation shows:

```typescript
import { attempt, isOk, map, flatMap } from '@deessejs/fp';
```

But `@deessejs/fp` does not export:
- `map` (standalone)
- `flatMap` (standalone)

What actually exists:

```typescript
import { attempt, attemptAsync } from '@deessejs/fp';
import { map as mapTry, flatMap as flatMapTry } from '@deessejs/fp';  // For Try
import { map as mapResult, flatMap as flatMapResult } from '@deessejs/fp';  // For Result
import { map as mapAsyncResult, flatMap as flatMapAsyncResult } from '@deessejs/fp';  // For AsyncResult
```

**Impact:** Users (including AI assistants) following the documentation will get immediate TypeScript errors like:
```
Module '"@deessejs/fp"' has no exported member 'map'.
```

## Problem 2: Three Nearly Identical APIs

The library has three sets of identical functions for three types:

| Operation | Try | Result | AsyncResult |
|-----------|-----|--------|-------------|
| Create | `attempt()` | `ok()`, `err()` | `okAsync()`, `errAsync()` |
| Transform | `map()` | `map()` | `map()` |
| Chain | `flatMap()` | `flatMap()` | `flatMap()` |
| Map Error | N/A | `mapErr()` | `mapErr()` |
| Tap | `tap()` | `tap()` | `tap()` |
| Extract | `getOrElse()` | `getOrElse()` | `getOrElse()` |

But they're **NOT re-exported as the same name**. Instead:

```typescript
// Try
import { attempt, attemptAsync, map, flatMap, tap, getOrElse, isOk, isErr } from '@deessejs/fp';

// Result
import { ok, err, mapResult, flatMapResult, mapErr, tapResult, getOrElseResult, isOk, isErr } from '@deessejs/fp';

// AsyncResult
import { okAsync, errAsync, mapAsyncResult, flatMapAsyncResult, mapErrAsyncResult, tapAsyncResult, getOrElseAsyncResult, isAsyncOk, isAsyncErr } from '@deessejs/fp';
```

**Impact:** Users must know which type they're working with and import the correctly suffixed function. This breaks IDE auto-import and makes the API hard to discover.

## Problem 3: Confusing Type Hierarchy

The relationship between types is unclear:

- `Try<T, E>` wraps sync functions that might throw
- `Result<T, E>` is for explicit success/failure
- `AsyncResult<T, E>` is for async operations

But `attemptAsync()` returns `Promise<Try<T, Error>>`, NOT `AsyncResult<T, E>`.

So:
```typescript
// attemptAsync returns Try, not AsyncResult
const result = await attemptAsync(() => fetch(url)); // Try<User, Error>

// To work with it, use Try's map (imported as mapTry or just map from try exports)
import { map } from '@deessejs/fp'; // Actually works for Try
const mapped = map(result, user => user.name);
```

This is confusing - `attemptAsync` creates a Try but the docs show using it with `flatMap` pattern which is for AsyncResult.

## Problem 4: Type Errors Are Unhelpful

When something goes wrong, TypeScript errors don't help identify the fix:

```
Argument of type 'Try<{ results: ... }, Error>' is not assignable to parameter of type 'Result<{ results: ... }, Error>'
```

This error doesn't tell you:
- Which function to use instead
- What the difference between Try and Result is in this context
- How to convert between them

## Recommendations

### 1. Unified API

Have ONE set of functions that work on all result types via TypeScript overloads or generics:

```typescript
// Single import, works everywhere
import { ok, err, map, flatMap, mapErr, tap, getOrElse, isOk, isErr, attempt, attemptAsync } from '@deessejs/fp';

// map works on Try, Result, and AsyncResult
const r1 = map(tryResult, transform);
const r2 = map(result, transform);
const r3 = await map(asyncResult, transform);
```

### 2. Fix Documentation

Every example in the docs should work with the actual exported API. Run the examples through TypeScript as part of CI.

### 3. Clear Type Hierarchy Documentation

Explain:
- When to use Try (wrapping throwing functions)
- When to use Result (explicit success/failure)
- When to use AsyncResult (async with error handling)
- How they relate to each other

### 4. Simplify Creation

```typescript
// Current: multiple ways to create "success"
ok(42);           // Result
okAsync(42);      // AsyncResult
attempt(() => 42); // Try (sync)
attemptAsync(() => fetch()); // Try (async) - confusingly returns Try, not AsyncResult

// Recommended: unify
success(42);       // Works for all
error('failed');   // Works for all
try_(() => 42);           // Try sync
tryAsync(() => fetch());  // Try async - should this return Try or AsyncResult?
```

## Conclusion

The library has good concepts but poor DX. The multiple similarly-named functions, documentation that doesn't match the code, and unclear type relationships make it frustrating to use. A unified API would significantly improve usability without losing functionality.

---

**Environment:**
- @deessejs/fp version: 3.1.1
- TypeScript version: 5.x
- Node.js version: 22.x
