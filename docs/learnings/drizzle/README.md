# Drizzle ORM - Table of Contents

This directory contains learning documents for Drizzle ORM.

## Documents

1. [Upsert & Increment Patterns](./upsert-increment.md) - `onConflictDoUpdate`, incrementing values, `excluded` keyword
2. [Batch & Transactions](./batch-transactions.md) - `db.batch()`, transactions, atomic operations
3. [Query Optimization](./query-optimization.md) - Prepared statements, select only needed columns, pagination, joins
4. [Schema Design](./schema-design.md) - Naming conventions, column types, indexes, JSONB, soft deletes
5. [Type Safety](./type-safety.md) - Type inference, `$inferSelect`, `$inferInsert`, Zod integration
6. [Connection & Error Handling](./connection-errors.md) - Pool configuration, error codes, SQL injection prevention

## Quick Reference

### Upsert Pattern (most common for usage tracking)
```typescript
await db.insert(dailyUsage)
  .values({ userId, date: today, searchCount: 1, totalCostUSD: costUSD })
  .onConflictDoUpdate({
    target: [dailyUsage.userId, dailyUsage.date],
    set: {
      searchCount: sql`${dailyUsage.searchCount} + 1`,
      totalCostUSD: sql`${dailyUsage.totalCostUSD} + ${costUSD}`,
    },
  });
```

### Increment
```typescript
sql`${table.column} + ${value}`
```

### Type Inference
```typescript
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;
```
