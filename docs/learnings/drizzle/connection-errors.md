# Connection & Error Handling

## Connection Pool Configuration

```typescript
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,                      // Maximum connections
  idleTimeoutMillis: 30000,     // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Fail fast
});

const db = drizzle(pool, {
  logger: process.env.NODE_ENV !== 'production', // Log queries in dev
});

// Handle pool errors
pool.on('error', (err) => {
  console.error('Unexpected pool error', err);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});
```

## Singleton Pattern (Avoid Multiple Instances)

```typescript
import { drizzle } from 'drizzle-orm/neon-http';
import type { NeonHttpDatabase } from 'drizzle-orm/neon-http';
import * as schema from './schema';

let db: NeonHttpDatabase<typeof schema> | null = null;

export function getDb() {
  if (!db) {
    db = drizzle({
      connection: process.env.DATABASE_URL!,
      schema,
    });
  }
  return db;
}

// Usage
import { getDb } from './db';
const db = getDb();
```

## Environment-Specific Configuration

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

const isProduction = process.env.NODE_ENV === 'production';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,

  // Production settings
  ssl: isProduction ? { rejectUnauthorized: false } : undefined,
  max: isProduction ? 20 : 5,

  // Development settings
  idleTimeoutMillis: isProduction ? 30000 : 10000,
});

const db = drizzle(pool, {
  logger: !isProduction,
});
```

## PostgreSQL Error Codes

Handle specific database errors:

```typescript
import { DatabaseError } from 'pg';

try {
  await db.insert(users).values({ email, name });
} catch (error) {
  if (error instanceof DatabaseError) {
    switch (error.code) {
      case '23505':
        // Unique constraint violation
        return { success: false, error: 'Email already exists' };
      case '23503':
        // Foreign key violation
        return { success: false, error: 'Referenced record does not exist' };
      case '23502':
        // Not null violation
        return { success: false, error: `Missing required field` };
      case '22P02':
        // Invalid text representation
        return { success: false, error: 'Invalid input format' };
    }
  }
  throw error;
}
```

## Transaction Error Handling

```typescript
import { users, posts } from './schema';

export async function createUserWithPost(
  userData: InsertModel<typeof users>,
  postData: Omit<InsertModel<typeof posts>, 'authorId'>
) {
  try {
    return await db.transaction(async (tx) => {
      // Create user
      const [user] = await tx.insert(users)
        .values(userData)
        .returning();

      // Create post
      const [post] = await tx.insert(posts)
        .values({ ...postData, authorId: user.id })
        .returning();

      return { user, post };
    });
  } catch (error) {
    // Transaction automatically rolled back
    console.error('Transaction failed:', error);
    throw error;
  }
}
```

## SQL Injection Prevention

Drizzle prevents SQL injection by default with parameterized queries:

```typescript
import { eq } from 'drizzle-orm';
import { users } from './schema';

// Safe: Parameterized automatically
const user = await db.select()
  .from(users)
  .where(eq(users.email, userInput));

// Dangerous: String interpolation - NEVER DO THIS
const dangerous = await db.execute(
  sql`SELECT * FROM users WHERE email = '${userInput}'` // SQL injection risk!
);

// Safe: Use sql template with parameters
const safe = await db.execute(
  sql`SELECT * FROM users WHERE email = ${userInput}` // Parameterized safely
);
```

## Prepared Statements Performance

```typescript
// Create once, reuse multiple times
const getUserById = db.select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

const user1 = await getUserById.execute({ id: 1 });
const user2 = await getUserById.execute({ id: 2 });
```

## Graceful Degradation

```typescript
export async function getUserWithFallback(userId: string) {
  try {
    // Try database first
    const user = await db.query.users.findFirst({
      where: eq(users.id, userId),
    });
    return user ?? fallbackUser;
  } catch (error) {
    // If DB fails, return fallback
    console.error('Database error, using fallback:', error);
    return fallbackUser;
  }
}
```

## Connection Pool Monitoring

```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});

// Log pool metrics
setInterval(() => {
  console.log({
    total: pool.totalCount,
    idle: pool.idleCount,
    waiting: pool.waitingCount,
  });
}, 10000);
```

## Key Takeaways

| Pattern | Usage |
|---------|-------|
| Pool `max` | Set to 20 for production |
| `idleTimeoutMillis` | 30s for production |
| Singleton `getDb()` | Avoid creating multiple instances |
| Error code `23505` | Unique constraint violation |
| Error code `23503` | Foreign key violation |
| Parameterized SQL | Drizzle handles this automatically |

## Sources

- [Drizzle Connection](https://orm.drizzle.team/docs/get-started-postgresql)
- [Drizzle Best Practices](https://drizzle-team-drizzle-orm.mintlify.app/guides/best-practices)
