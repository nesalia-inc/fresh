# Batch & Transactions

## Batch API

Execute multiple queries in a single database round trip. Reduces network latency.

```typescript
const [usersResult, postsResult, commentsResult] = await db.batch([
  db.select().from(users),
  db.select().from(posts),
  db.select().from(comments),
]);
```

**Supported for:** LibSQL, Neon, D1

> For PostgreSQL (via `pg`), use transactions instead.

## Transactions

Wrap multiple operations in an atomic transaction:

```typescript
const result = await db.transaction(async (tx) => {
  // All operations use the same transaction
  const [user] = await tx.insert(users).values(userData).returning();
  const [post] = await tx.insert(posts).values({ ...postData, authorId: user.id }).returning();
  return { user, post };
});
// Automatically rolled back if any operation fails
```

### When to Use Transactions

- Multi-step operations that need atomicity (e.g., create user + create post)
- Operations where partial success would leave data in invalid state
- Batch updates that should succeed or fail together

### Nested Transactions (Savepoints)

Drizzle supports savepoints for nested transactions:

```typescript
await db.transaction(async (tx) => {
  await tx.insert(users).values({ email: 'test@example.com' });

  // Nested transaction with savepoint
  await tx.transaction(async (nestedTx) => {
    await nestedTx.insert(posts).values({ title: 'My Post' });
  });

  // If nestedTx fails, only its changes are rolled back
  // If outer tx fails, everything is rolled back
});
```

## Batch vs Transactions

| Feature | Batch | Transaction |
|---------|-------|-------------|
| Network round trips | 1 | 1 |
| Atomicity | No (individual failures) | Yes (all or nothing) |
| Rollback on failure | No | Yes |
| Supported drivers | Neon, LibSQL, D1 | All |
| Use case | Read multiple tables, independent inserts | Related operations needing atomicity |

## Real Example: Record Usage + Update Quota

For the fresh-final project, we might want to record usage and update quota atomically:

```typescript
import { db } from "@/db";
import { dailyUsage, userQuota } from "@/db/schema";
import { eq, sql } from "drizzle-orm";

export async function recordUsageAndUpdateQuota(params: {
  userId: string;
  action: "search" | "fetch";
  costUSD: number;
}) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  await db.transaction(async (tx) => {
    // 1. Record daily usage
    await tx.insert(dailyUsage)
      .values({
        userId: params.userId,
        date: today,
        searchCount: params.action === "search" ? 1 : 0,
        fetchCount: params.action === "fetch" ? 1 : 0,
        totalCostUSD: params.costUSD.toFixed(6),
      })
      .onConflictDoUpdate({
        target: [dailyUsage.userId, dailyUsage.date],
        set: {
          searchCount: sql`${dailyUsage.searchCount} + ${params.action === "search" ? 1 : 0}`,
          fetchCount: sql`${dailyUsage.fetchCount} + ${params.action === "fetch" ? 1 : 0}`,
          totalCostUSD: sql`${dailyUsage.totalCostUSD} + ${params.costUSD}`,
        },
      });

    // 2. Update monthly quota
    await tx.update(userQuota)
      .set({
        ...(params.action === "search"
          ? { currentMonthSearches: sql`${userQuota.currentMonthSearches} + 1` }
          : { currentMonthFetches: sql`${userQuota.currentMonthFetches} + 1` }
        ),
        currentMonthCostUSD: sql`${userQuota.currentMonthCostUSD} + ${params.costUSD}`,
      })
      .where(eq(userQuota.userId, params.userId));
  });
}
```

## Sources

- [Drizzle Batch API](https://orm.drizzle.team/docs/batch-api)
- [Drizzle Transactions](https://orm.drizzle.team/docs/core/transactions)
