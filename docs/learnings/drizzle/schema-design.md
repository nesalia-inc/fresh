# Schema Design

## Naming Conventions

| Object | Convention | Example |
|--------|------------|---------|
| Table names | plural, snake_case | `users`, `blog_posts` |
| Column names | snake_case in DB | `user_id`, `created_at` |
| TypeScript variables | camelCase | `users`, `blogPosts` |

```typescript
// Good
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  firstName: text('first_name'),
  lastName: text('last_name'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

// Avoid: Inconsistent naming
export const Users = pgTable('user', { // Mixed naming
  ID: serial('user_id').primaryKey(),   // camelCase in DB
  EmailAddress: text('email'),          // PascalCase in DB
});
```

## Column Types

Choose the most appropriate column type:

```typescript
import {
  pgTable,
  serial,
  text,
  varchar,
  integer,
  boolean,
  timestamp,
  jsonb,
  decimal,
} from 'drizzle-orm/pg-core';

export const products = pgTable('products', {
  id: serial('id').primaryKey(),

  // Specific length for known limits
  sku: varchar('sku', { length: 50 }).notNull().unique(),

  // Unlimited content
  description: text('description'),

  // Appropriate numeric types
  price: decimal('price', { precision: 10, scale: 2 }).notNull(),
  stock: integer('stock').notNull().default(0),

  // Boolean for true/false states
  isActive: boolean('is_active').notNull().default(true),

  // JSONB for structured data
  metadata: jsonb('metadata').$type<{
    color?: string;
    size?: string;
    tags?: string[];
  }>(),

  // Timestamp with timezone
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
});
```

## Decimal Precision for Money/Currency

For Exa API micro-pricing:

```typescript
// Good: scale: 6 for micro-pricing
costUSD: decimal('cost_usd', {
  precision: 10,
  scale: 6
}).notNull().default("0"),
```

## Indexes

Always add indexes to foreign keys and frequently queried columns:

```typescript
export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  status: text('status').notNull().default('draft'),
}, (table) => ({
  // Index foreign keys
  authorIdIdx: index('author_id_idx').on(table.authorId),

  // Index frequently filtered columns
  statusIdx: index('status_idx').on(table.status),

  // Composite index for common query patterns
  authorStatusIdx: index('author_status_idx').on(
    table.authorId,
    table.status
  ),
}));
```

## Composite Index for Upsert Target

For `dailyUsage` table that needs upsert by user+date:

```typescript
export const dailyUsage = pgTable("daily_usage", {
  id: integer("id").primaryKey().autoIncrement(),
  userId: text("user_id").notNull(),
  date: timestamp("date").notNull(),
  searchCount: integer("search_count").notNull().default(0),
  fetchCount: integer("fetch_count").notNull().default(0),
  totalCostUSD: decimal("total_cost_usd", { precision: 10, scale: 6 }).notNull().default("0"),
}, (table) => [
  // Composite unique index for upsert target
  index("daily_usage_user_date_idx").on(table.userId, table.date),
])
```

## Timestamps Pattern

```typescript
// Standard timestamps
createdAt: timestamp('created_at', { withTimezone: true })
  .notNull()
  .defaultNow(),

// Auto-updating timestamp
updatedAt: timestamp('updated_at', { withTimezone: true })
  .notNull()
  .defaultNow()
  .$onUpdate(() => new Date()),
```

## Soft Deletes

```typescript
import { pgTable, serial, text, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  deletedAt: timestamp('deleted_at', { withTimezone: true }),
});

// Helper to filter deleted records
import { isNull } from 'drizzle-orm';

export function withoutDeleted() {
  return isNull(users.deletedAt);
}

// Usage
const activeUsers = await db.select()
  .from(users)
  .where(withoutDeleted());
```

## JSONB Type-Safe Columns

```typescript
interface UserPreferences {
  theme: 'light' | 'dark';
  notifications: {
    email: boolean;
    push: boolean;
  };
  language: string;
}

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  preferences: jsonb('preferences')
    .$type<UserPreferences>()
    .notNull()
    .default({
      theme: 'light',
      notifications: { email: true, push: false },
      language: 'en',
    }),
});

// TypeScript knows the structure
const user = await db.select().from(users).limit(1);
const theme = user[0].preferences.theme; // Type: 'light' | 'dark'
```

## Usage Tracking Schema (Real Example)

```typescript
// dailyUsage - aggregated daily usage for billing
export const dailyUsage = pgTable("daily_usage", {
  id: integer("id").primaryKey().autoIncrement(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  date: timestamp("date").notNull(), // Midnight of the day
  searchCount: integer("search_count").notNull().default(0),
  fetchCount: integer("fetch_count").notNull().default(0),
  totalCostUSD: decimal("total_cost_usd", { precision: 10, scale: 6 }).notNull().default("0"),
  updatedAt: timestamp("updated_at").defaultNow().$onUpdate(() => new Date()),
}, (table) => [
  index("daily_usage_user_date_idx").on(table.userId, table.date),
]);

// userQuota - monthly limits per user
export const userQuota = pgTable("user_quota", {
  id: integer("id").primaryKey().autoIncrement(),
  userId: text("user_id")
    .notNull()
    .unique()
    .references(() => user.id, { onDelete: "cascade" }),
  tier: text("tier", { enum: ["free", "pro", "enterprise"] }).notNull().default("free"),
  monthlySearchLimit: integer("monthly_search_limit").notNull().default(100),
  monthlyFetchLimit: integer("monthly_fetch_limit").notNull().default(50),
  monthlyCostLimitUSD: decimal("monthly_cost_limit_usd", { precision: 10, scale: 2 }).notNull().default("10.00"),
  currentMonthSearches: integer("current_month_searches").notNull().default(0),
  currentMonthFetches: integer("current_month_fetches").notNull().default(0),
  currentMonthCostUSD: decimal("current_month_cost_usd", { precision: 10, scale: 6 }).notNull().default("0"),
  periodStart: timestamp("period_start").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().$onUpdate(() => new Date()),
});
```

## Sources

- [Drizzle Schema Guide](https://orm.drizzle.team/docs/schema-overview)
- [Drizzle Best Practices](https://drizzle-team-drizzle-orm.mintlify.app/guides/best-practices)
