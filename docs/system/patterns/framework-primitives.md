# Framework Primitives

Building blocks with built-in gates.

## The Vision

Every common building block should be a primitive with gates:

```
Every primitive has THREE gates:
1. COMPILE TIME: Types enforce correct usage
2. RUNTIME: Middleware intercepts calls
3. PR TIME (AST): Verifies all access points use primitive
```

## Example: RBAC Primitive

```
1. DEFINE permissions as code:
const Permissions = {
  USER_READ: 'user:read',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
};

2. DEFINE roles:
const Roles = {
  ADMIN: ['*'],
  MANAGER: [
    Permissions.USER_READ,
    Permissions.USER_CREATE,
    Permissions.USER_UPDATE,
    Permissions.ORDER_CREATE,
  ],
  USER: [Permissions.USER_READ],
};

3. VERIFY at compile time:
@RequirePermission(Permissions.USER_CREATE)
async function createUser(req) { ... }

4. VERIFY at runtime:
Gate intercepts every request:
- Check user has required permission
- Log access attempt
- Block if denied

5. VERIFY at PR time (AST gate):
- Every @RequirePermission must have a test
- Every permission must be used
- No hardcoded permission checks
- All roles tested
```

## Frontend Performance Primitives

```
1. Layout Shift Detection:
<Image src="..." width={800} height={600} />
Gate verifies:
- Has width/height
- Has loading="lazy" for below-fold

2. CSS Performance:
- No unused CSS
- No expensive selectors

3. Bundle Size:
- No new packages > 10KB
- Bundle size < threshold
```

## Complete Primitive List

```
AUTHENTICATION:
- Login/logout flows
- Token management (JWT, refresh, rotation)
- Multi-factor authentication

AUTHORIZATION (RBAC/ABAC):
- Permission definitions
- Role definitions
- Policy engine
- Audit logging

DATA ACCESS:
- Repository pattern
- Query builders
- Pagination
- Soft deletes

VALIDATION:
- Input validation (schema-based)
- Cross-field validation
- Async validation

ERROR HANDLING:
- Error codes
- User-facing errors
- Recovery strategies

CACHING:
- Cache strategies (cache-aside, write-through)
- Invalidation patterns

NOTIFICATIONS:
- Channel abstraction
- Template system

PAYMENTS:
- Provider abstraction
- Webhook handling
- Idempotency

SEARCH:
- Query abstraction
- Faceted search
- Pagination
```

---

*Last updated: 2026-03-04*
