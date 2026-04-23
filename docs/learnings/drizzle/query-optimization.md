# Query Optimization

## Prepared Statements

Create prepared statements for frequently executed queries. Improves performance by caching the query plan.

```typescript
const getUserById = db.select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

// Execute multiple times efficiently
const user1 = await getUserById.execute({ id: 1 });
const user2 = await getUserById.execute({ id: 2 });
const user3 = await getUserById.execute({ id: 3 });
```

## Select Only Needed Columns

Avoid fetching entire rows when you only need specific fields:

```typescript
// Bad: Fetches all columns
const allUsers = await db.select().from(users);

// Good: Select only what you need
const userEmails = await db.select({
  id: users.id,
  email: users.email,
}).from(users);

// Good: Computed columns with aggregation
const userStats = await db.select({
  userId: users.id,
  userName: users.name,
  postCount: count(posts.id),
})
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))
  .groupBy(users.id);
```

## Pagination

### Offset-based (Simple but Slow for Large Offsets)

```typescript
export async function getPostsOffset(page: number, pageSize: number) {
  return await db.select()
    .from(posts)
    .orderBy(desc(posts.createdAt))
    .limit(pageSize)
    .offset(page * pageSize);
}
```

### Cursor-based (Recommended for Large Datasets)

```typescript
export async function getPostsCursor(cursor: number | null, pageSize: number) {
  const query = db.select()
    .from(posts)
    .orderBy(desc(posts.id))
    .limit(pageSize + 1); // Fetch one extra to check if there's more

  if (cursor) {
    query.where(gt(posts.id, cursor));
  }

  const results = await query;
  const hasMore = results.length > pageSize;
  const items = hasMore ? results.slice(0, -1) : results;

  return {
    items,
    nextCursor: hasMore ? items[items.length - 1].id : null,
  };
}
```

## Efficient Joins

### Avoid N+1 Queries

```typescript
// Bad: N+1 query problem
const users = await db.select().from(usersTable);
for (const user of users) {
  user.posts = await db.select()
    .from(posts)
    .where(eq(posts.authorId, user.id));
}

// Good: Use relational queries
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: true,
  },
});

// Good: Manual join when you need control
const usersWithPostCount = await db.select({
  id: users.id,
  name: users.name,
  postCount: count(posts.id),
})
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))
  .groupBy(users.id);
```

## Aggregations with `groupBy`

```typescript
import { sql } from 'drizzle-orm';

const daily = await db
  .select({
    date: dailyUsage.date,
    searches: sql<number>`SUM(${dailyUsage.searchCount})`,
    cost: sql<number>`SUM(CAST(${dailyUsage.totalCostUSD} AS numeric))`,
  })
  .from(dailyUsage)
  .groupBy(dailyUsage.date)
  .orderBy(dailyUsage.date);
```

## Count Utility

Drizzle provides `db.$count()` as a shortcut for `COUNT(*)`:

```typescript
const total = await db.$count(users);
const filtered = await db.$count(users, eq(users.name, "Dan"));
```

## Query Execution Time Monitoring

```typescript
export async function withTiming<T>(
  queryFn: () => Promise<T>,
  queryName: string
): Promise<T> {
  const start = Date.now();
  try {
    const result = await queryFn();
    const duration = Date.now() - start;
    console.log(`${queryName} took ${duration}ms`);
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    console.error(`${queryName} failed after ${duration}ms:`, error);
    throw error;
  }
}

// Usage
const users = await withTiming(
  () => db.select().from(usersTable),
  'fetch_all_users'
);
```

## Custom Logger for Slow Queries

```typescript
import { DefaultLogger } from 'drizzle-orm';

class PerformanceLogger extends DefaultLogger {
  override logQuery(query: string, params: unknown[]): void {
    const start = Date.now();
    super.logQuery(query, params);

    // Log slow queries (>100ms)
    setTimeout(() => {
      const duration = Date.now() - start;
      if (duration > 100) {
        console.warn(`Slow query (${duration}ms):`, query);
      }
    }, 0);
  }
}

const db = drizzle(pool, {
  logger: new PerformanceLogger(),
});
```

## Performance Tips Summary

| Technique | Benefit |
|-----------|---------|
| Prepared statements | Reuse query plan, faster execution |
| Select only needed | Less memory, faster transfer |
| Cursor pagination | O(1) vs O(n) for large offsets |
| Avoid N+1 | Single query vs N+1 queries |
| `db.$count()` | Simpler than `COUNT(*)` |
| Composite indexes | Faster lookups for common query patterns |

## Sources

- [Drizzle Select](https://orm.drizzle.team/docs/select)
- [Drizzle Best Practices](https://drizzle-team-drizzle-orm.mintlify.app/guides/best-practices)
