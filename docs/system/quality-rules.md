# Code Quality Rules Specification

Detailed specification of all quality rules that should be enforced on agent-generated code.

---

## Rule Categories

### Category 1: Error Handling (25%)

These rules ensure errors are handled properly and visible to users.

#### Rule 1.1: No Silent Failures

**ID:** `no-silent-failures`

**Description:** All async functions must have proper error handling that is visible to users.

**Pattern Required:**
```typescript
async function fetchData() {
  try {
    const result = await api.get('/data');
    return result;
  } catch (error) {
    // Must log for debugging
    logger.error('fetchData failed', { error });
    // Must throw user-friendly error
    throw new DataFetchError('Failed to load data. Please try again.');
  }
}
```

**Anti-Pattern (fails):**
```typescript
async function fetchData() {
  const result = await api.get('/data'); // No try/catch
  return result;
}

// Or:
async function fetchData() {
  try {
    return await api.get('/data');
  } catch (error) {
    // Silent failure - user never knows
    return null;
  }
}
```

#### Rule 1.2: User-Visible Errors

**ID:** `user-visible-errors`

**Description:** Errors must show a meaningful message to the user, not just be logged.

**Pattern
// Component Required:**
```typescript must show error to user
function UserProfile({ userId }) {
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser(userId)
      .catch(err => {
        setError('Failed to load profile. Please refresh.');
        logger.error(err);
      });
  }, [userId]);

  if (error) return <ErrorMessage>{error}</ErrorMessage>;
  // ...
}
```

#### Rule 1.3: Loading States

**ID:** `loading-states`

**Description:** Every async operation must have a loading state visible to users.

**Pattern Required:**
```typescript
function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetchUsers()
      .then(setUsers)
      .catch(err => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage>{error}</ErrorMessage>;
  return <UserListView users={users} />;
}
```

---

### Category 2: Function Quality (25%)

#### Rule 2.1: Maximum Function Length

**ID:** `max-function-length`

**Description:** Functions must not exceed 30 lines.

**Measurement:** Count lines between function declaration and closing brace.

**Pattern Required:**
```typescript
// ❌ BAD (45 lines):
async function processOrder(order: OrderInput) {
  // 45 lines of code
}

// ✅ GOOD:
async function processOrder(order: OrderInput) {
  const validated = await validateOrder(order);
  const priced = await calculatePrice(validated);
  const inventory = await checkInventory(priced);
  const created = await createOrder(inventory);
  await sendConfirmationEmail(created);
  await updateAnalytics(created);
  return created;
}
```

#### Rule 2.2: Single Responsibility

**ID:** `single-responsibility`

**Description:** Each function should do one thing.

**Pattern Required:**
```typescript
// ✅ GOOD: Separate functions
function validateOrder(order: OrderInput): ValidatedOrder { /* ... */ }
function calculatePrice(order: ValidatedOrder): Price { /* ... */ }
function checkInventory(price: Price): InventoryCheck { /* ... */ }
function createOrder(check: InventoryCheck): Order { /* ... */ }
```

**Anti-Pattern (fails):**
```typescript
// ❌ BAD: One function does everything
async function processOrder(order) {
  // validates
  // calculates prices
  // checks inventory
  // creates order
  // sends email
  // updates analytics
  // returns result
}
```

#### Rule 2.3: Early Returns

**ID:** `early-returns`

**Description:** Use guard clauses to reduce nesting.

**Pattern Required:**
```typescript
function processUser(user: User | null) {
  // Guard clause - early return
  if (!user) {
    throw new UserNotFoundError();
  }

  // Main logic - no nesting from null check
  const normalized = normalizeUser(user);
  return transformUser(normalized);
}
```

**Anti-Pattern (fails):**
```typescript
function processUser(user) {
  if (user) { // ❌ Nested
    if (user.isActive) { // ❌ More nesting
      if (user.hasPermission) { // ❌ Even more
        // Actual logic here
      }
    }
  }
}
```

#### Rule 2.4: No Magic Numbers

**ID:** `no-magic-numbers`

**Description:** All numbers must be defined as constants.

**Pattern Required:**
```typescript
// constants.ts
export const API_TIMEOUT_MS = 5000;
export const MAX_RETRY_ATTEMPTS = 3;
export const PAGE_SIZE = 20;
export const DEBOUNCE_MS = 300;

// usage.ts
const response = await fetch(url, { timeout: API_TIMEOUT_MS });
```

**Anti-Pattern (fails):**
```typescript
// Magic numbers - what do these mean?
await fetch(url, { timeout: 5000 });
if (attempts === 3) { /* ... */ }
```

---

### Category 3: Testing Quality (20%)

#### Rule 3.1: No All Mocks

**ID:** `no-all-mocks`

**Description:** Tests cannot mock everything. Must have real implementations.

**Pattern Required:**
```typescript
// ✅ GOOD: Real implementation with some mocks
describe('OrderService', () => {
  it('creates order successfully', async () => {
    // Mock external API (OK)
    const mockDb = mock<OrderDatabase>();
    mockDb.save.mockResolvedValue({ id: '1' });

    // Use real service (not mocked)
    const service = new OrderService(mockDb);

    const order = await service.createOrder(validOrder);

    expect(order.id).toBe('1');
    expect(mockDb.save).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'pending' })
    );
  });
});
```

**Anti-Pattern (fails):**
```typescript
// ❌ BAD: Everything mocked
describe('OrderService', () => {
  it('creates order', async () => {
    mockOrderService.createOrder.mockResolvedValue({ id: '1' });
    const order = await orderService.createOrder({});
    expect(order.id).toBe('1');
  });
});
```

#### Rule 3.2: Edge Case Tests

**ID:** `edge-case-tests`

**Description:** Must test null, empty, and error states.

**Pattern Required:**
```typescript
describe('fetchUser', () => {
  it('fetches user successfully', () => { /* ... */ });
  it('handles null response', () => { /* ... */ });
  it('handles network error', () => { /* ... */ });
  it('handles timeout', () => { /* ... */ });
  it('handles unauthorized', () => { /* ... */ });
  it('handles empty database', () => { /* ... */ });
});
```

#### Rule 3.3: Integration Tests Required

**ID:** `integration-tests-required`

**Description:** Must have at least one integration test per feature.

**Pattern:**
- End-to-end test of key user flows
- Tests multiple components working together
- Tests real data flow

---

### Category 4: Architecture (15%)

#### Rule 4.1: Separation of Concerns

**ID:** `separation-of-concerns`

**Description:** UI components must be separate from business logic.

**Pattern Required:**
```typescript
// ✅ GOOD: Logic in hook
function UserList() {
  const { users, isLoading, error } = useUsers();
  // UI only
  if (isLoading) return <Skeleton />;
  return <ul>{users.map(u => <li>{u.name}</li>)}</ul>;
}

// useUsers.ts - Business logic
function useUsers() {
  const [users, setUsers] = useState([]);
  // Fetch logic here, not in component
}
```

**Anti-Pattern (fails):**
```typescript
// ❌ BAD: Logic in component
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/users') // Logic in UI component
      .then(r => r.json())
      .then(setUsers);
  }, []);

  return <ul>{users.map(/* ... */)}</ul>;
}
```

#### Rule 4.2: Dependency Injection

**ID:** `dependency-injection`

**Description:** No hard dependencies. Use DI.

**Pattern Required:**
```typescript
// ✅ GOOD: DI
class UserService {
  constructor(private api: ApiClient, private logger: Logger) {}

  async fetchUser(id: string) {
    try {
      return await this.api.get(`/users/${id}`);
    } catch (e) {
      this.logger.error(e);
      throw e;
    }
  }
}

// Usage:
const service = new UserService(new HttpApi(), new ConsoleLogger());
```

**Anti-Pattern (fails):**
```typescript
// ❌ BAD: Hard dependency
class UserService {
  async fetchUser(id: string) {
    return fetch(`/api/users/${id}`); // Hardcoded fetch
  }
}
```

---

### Category 5: Security (15%)

#### Rule 5.1: Input Validation

**ID:** `input-validation`

**Description:** All external input must be validated.

**Pattern Required:**
```typescript
// ✅ GOOD: Validation with Zod
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().positive().optional(),
});

async function createUser(data: unknown) {
  const validated = CreateUserSchema.parse(data); // Validates
  // Use validated data
}
```

#### Rule 5.2: No Sensitive Data in Logs

**ID:** `no-sensitive-data-logs`

**Description:** Never log passwords, tokens, or PII.

**Pattern Required:**
```typescript
// ✅ GOOD: Sanitized logging
logger.info('User logged in', {
  userId: user.id,
  email: user.email, // Not password
});
```

**Anti-Pattern (fails):**
```typescript
// ❌ BAD: Logs sensitive data
logger.info('Login', { password: user.password }); // NEVER
logger.info('API Key', { key: apiKey }); // NEVER
```

---

## Quality Score Calculation

### Weights

| Category | Weight | Rules |
|----------|--------|-------|
| Error Handling | 25% | 3 rules |
| Function Quality | 25% | 4 rules |
| Testing Quality | 20% | 3 rules |
| Architecture | 15% | 2 rules |
| Security | 15% | 2 rules |

### Score Per Rule

```
rule_score = (passing_checks / total_checks) * 100
category_score = sum(rule_scores) / number_of_rules
overall_score = sum(category_scores * category_weight)
```

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | ✅ Excellent | Allow |
| 80-89 | ⚠️ Good | Allow with warnings |
| 70-79 | ❌ Needs Work | Block, show issues |
| <70 | ❌❌ Poor | Block + require rewrite |

---

## Implementation Example

### Quality Scanner Interface

```typescript
interface QualityRule {
  id: string;
  name: string;
  category: 'error-handling' | 'function-quality' | 'testing' | 'architecture' | 'security';
  check: (context: QualityContext) => QualityResult;
}

interface QualityResult {
  passed: boolean;
  score: number; // 0-100 for this rule
  issues: QualityIssue[];
}

interface QualityIssue {
  ruleId: string;
  severity: 'error' | 'warning' | 'suggestion';
  message: string;
  location: { file: string; line: number };
  suggestion?: string;
}

interface QualityReport {
  overallScore: number;
  categoryScores: Record<string, number>;
  issues: QualityIssue[];
  passed: boolean;
}
```

### Running Quality Check

```typescript
async function checkQuality(code: string): Promise<QualityReport> {
  const rules: QualityRule[] = [
    noSilentFailuresRule,
    userVisibleErrorsRule,
    loadingStatesRule,
    maxFunctionLengthRule,
    singleResponsibilityRule,
    // ... more rules
  ];

  const issues: QualityIssue[] = [];
  const categoryScores: Record<string, number[]> = {};

  for (const rule of rules) {
    const result = await rule.check({ code });
    issues.push(...result.issues);

    if (!categoryScores[rule.category]) {
      categoryScores[rule.category] = [];
    }
    categoryScores[rule.category].push(result.score);
  }

  const categoryAverages = Object.entries(categoryScores).reduce(
    (acc, [category, scores]) => ({
      ...acc,
      [category]: scores.reduce((a, b) => a + b, 0) / scores.length,
    }),
    {}
  );

  const overallScore = calculateOverallScore(categoryAverages);

  return {
    overallScore,
    categoryScores: categoryAverages,
    issues,
    passed: overallScore >= 80,
  };
}
```

---

## Conclusion

This specification defines a comprehensive quality system that goes far beyond what linters and type checkers can enforce. It ensures that agent-generated code:

1. **Handles errors properly** - Users see meaningful errors
2. **Is maintainable** - Small, focused functions
3. **Is testable** - Real tests, not just mocks
4. **Is well-architected** - Separated concerns, DI
5. **Is secure** - Input validation, no data leaks

Only by enforcing all these rules can we ensure agents produce production-quality code.

---

*Document version: 1.0*
*Last updated: 2026-03-04*
