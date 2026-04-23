# Type Safety

## Type Inference from Schema

Always infer types from your schema instead of manual typing:

```typescript
import { users } from './schema';

type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;

// Use in functions
export async function createUser(data: NewUser): Promise<User> {
  const [user] = await db.insert(users).values(data).returning();
  return user;
}

// For partial updates
type UserUpdate = Partial<NewUser>;

export async function updateUser(
  id: number,
  data: UserUpdate
): Promise<User> {
  const [user] = await db.update(users)
    .set(data)
    .where(eq(users.id, id))
    .returning();
  return user;
}
```

## Custom Type Helpers

Create reusable type utilities:

```typescript
import type { InferSelectModel, InferInsertModel } from 'drizzle-orm';

// Generic helpers
export type SelectModel<T extends AnyTable> = InferSelectModel<T>;
export type InsertModel<T extends AnyTable> = InferInsertModel<T>;

// Make all fields optional for updates
export type UpdateModel<T> = Partial<InsertModel<T>>;

// Pick specific fields
export type UserPublic = Pick<SelectModel<typeof users>, 'id' | 'name' | 'email'>;

// Omit sensitive fields
export type UserSafe = Omit<SelectModel<typeof users>, 'passwordHash'>;
```

## Zod Integration

Combine Drizzle with Zod for runtime validation:

```typescript
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { z } from 'zod';
import { users } from './schema';

// Generate Zod schemas from Drizzle tables
const insertUserSchema = createInsertSchema(users, {
  // Customize validation
  email: z.string().email(),
  name: z.string().min(2).max(100),
});

const selectUserSchema = createSelectSchema(users);

// Use for API validation
export async function createUserApi(input: unknown) {
  // Validate input
  const validated = insertUserSchema.parse(input);

  // Insert with validated data
  const [user] = await db.insert(users)
    .values(validated)
    .returning();

  return user;
}
```

## Return Types from Operations

```typescript
// Insert returns the inserted row
const [user] = await db.insert(users).values({ email, name }).returning();
// user type: typeof users.$inferSelect

// Update returns the updated row
const [updated] = await db.update(users).set({ name: 'New' }).where(eq(users.id, 1)).returning();

// Delete returns the deleted row
const [deleted] = await db.delete(users).where(eq(users.id, 1)).returning();

// Select returns array
const allUsers: typeof users.$inferSelect[] = await db.select().from(users);
```

## Type-Safe JSON Columns

```typescript
import { jsonb } from 'drizzle-orm/pg-core';

// Define your JSON structure
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
    .$type<UserPreferences>() // Type-safe JSON
    .notNull()
    .default({
      theme: 'light',
      notifications: { email: true, push: false },
      language: 'en',
    }),
});

// TypeScript knows the structure
const user = await db.select().from(users).limit(1);
const theme: 'light' | 'dark' = user[0].preferences.theme;
```

## SQL Template Type Safety

```typescript
import { sql } from 'drizzle-orm';

// Type helper for return types
const totalCost = sql<number>`SUM(CAST(${dailyUsage.totalCostUSD} AS numeric))`;

// Safe: Parameterized automatically
await db.execute(sql`SELECT * FROM users WHERE id = ${userId}`);
```

## Relation Types

```typescript
import { relations } from 'drizzle-orm';

export const userRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  accounts: many(accounts),
}));

export const postRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));

// Type-safe relations
const userWithPosts = await db.query.users.findFirst({
  with: {
    posts: true,  // Type: Post[]
  },
});

const postAuthor = userWithPosts?.posts[0]?.author; // Type: User | undefined
```

## Generic Query Functions

```typescript
export async function findById<T extends typeof users>(
  table: T,
  id: number
): Promise<InferSelectModel<T> | undefined> {
  const [result] = await db
    .select()
    .from(table)
    .where(eq(table.id, id));
  return result;
}

const user = await findById(users, 1);
const post = await findById(posts, 1);
```

## Key Takeaways

| Pattern | Syntax |
|---------|--------|
| Get select type | `typeof table.$inferSelect` |
| Get insert type | `typeof table.$inferInsert` |
| JSONB type-safe | `. $type<T>()` |
| Zod from schema | `createInsertSchema()`, `createSelectSchema()` |
| SQL with types | `sql<T>` |

## Sources

- [Drizzle Type Safety](https://orm.drizzle.team/docs/type-safety)
- [drizzle-zod](https://github.com/drizzle-team/drizzle-orm/tree/master/drizzle-zod)
