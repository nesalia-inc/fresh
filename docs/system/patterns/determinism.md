# Reducing Mental Load Through Determinism

Goal: Make the "right thing" the EASY thing.

## The Problem: Cognitive Overhead

When an agent writes code, they must think about:
- What is this function supposed to do?
- What are the edge cases?
- How does this handle errors?
- What happens if X is null?
- What if the API call fails?
- How does this scale?
- What if the database is down?

This leads to forgotten edge cases, silent failures, and bugs.

## Category Theory: Composition as Core

```
If A → B and B → C, then A → C

In code:
const getEnrichedUser = compose(enrichUser, fetchUser);

Less thinking, more correct
```

## Automata Theory: State Machines

```
Instead of ad-hoc state:
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

Use explicit state machine:
type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: Data }
  | { status: 'error'; error: Error; retryCount: number };
```

## Practical Patterns

### Railway-Oriented Programming

```
Instead of:
function processUser(input) {
  const user = validate(input);
  if (!user.valid) return null;
  const saved = save(user);
  if (!saved) return null;
  const enriched = enrich(saved);
  if (!enriched) return null;
  return enriched;
}

Write:
const processUser = (input) =>
  Result.of(input)
    .map(validate)
    .map(save)
    .map(enrich)
    .extract();
```

### Contract-Based Design

```
interface UserService {
  // PRECONDITIONS:
  // - id must be non-empty string
  // - caller must have 'read:users' permission
  getUser(id: string): Promise<User>;

  // PRECONDITIONS:
  // - user must pass validation
  // - caller must have 'write:users' permission
  createUser(data: CreateUserDTO): Promise<User>;
}
```

### Effect Schema

```
const Effects = {
  fetchUser: t.function([t.string], User),
  saveUser: t.function([User], User),
  sendEmail: t.function([Email], void),
};

// Runtime validates:
// - fetchUser called with string, returns User
// - saveUser called with User, returns User
// - sendEmail called with Email, returns void
```

## Summary: 5 Ways to Reduce Mental Load

1. **Deterministic patterns** - Same input → same output
2. **Composable abstractions** - Chain transformations
3. **Explicit state machines** - No impossible states
4. **Contracts** - Pre/postconditions explicit
5. **Effect systems** - Effects as data

Result: Agent focuses on BUSINESS LOGIC, not boilerplate

---

*Last updated: 2026-03-04*
