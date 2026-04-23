# Upsert & Increment Patterns

## Upsert with `onConflictDoUpdate`

Insert a row, or update it if it already exists:

```typescript
await db
  .insert(users)
  .values({ id: 1, name: 'John' })
  .onConflictDoUpdate({
    target: users.id,
    set: { name: 'Super John' },
  });
```

Generates:
```sql
insert into users ("id", "name") values (1, 'John')
  on conflict ("id") do update set name = 'Super John';
```

## Composite Target

For tables with composite primary keys or unique indexes:

```typescript
await db
  .insert(inventory)
  .values({ warehouseId: 1, productId: 1, quantity: 100 })
  .onConflictDoUpdate({
    target: [inventory.warehouseId, inventory.productId],
    set: { quantity: sql`${inventory.quantity} + 100` },
  });
```

## Incrementing Values with `sql`

Use the `sql` template tag to increment counters on conflict:

```typescript
await db.insert(dailyUsage)
  .values({
    userId: userId,
    date: today,
    searchCount: 1,
    totalCostUSD: costUSD,
  })
  .onConflictDoUpdate({
    target: [dailyUsage.userId, dailyUsage.date],
    set: {
      searchCount: sql`${dailyUsage.searchCount} + 1`,
      totalCostUSD: sql`${dailyUsage.totalCostUSD} + ${costUSD}`,
    },
  });
```

**Key pattern for billing/usage aggregation.**

## Increment Utility Function

```typescript
import { AnyColumn } from 'drizzle-orm';

const increment = (column: AnyColumn, value = 1) => {
  return sql`${column} + ${value}`;
};

// Usage
await db.update(table)
  .set({
    counter1: increment(table.counter1),
    counter2: increment(table.counter2, 10),
  })
  .where(eq(table.id, 1));
```

## Update with Increment

Simple increment on existing rows:

```typescript
await db
  .update(userQuota)
  .set({
    currentMonthSearches: sql`${userQuota.currentMonthSearches} + 1`,
    currentMonthCostUSD: sql`${userQuota.currentMonthCostUSD} + ${costUSD}`,
  })
  .where(eq(userQuota.userId, userId));
```

## Using `excluded` Keyword

The `excluded` pseudo-table references the row that was proposed for insertion:

```typescript
import { sql } from 'drizzle-orm';

await db
  .insert(users)
  .values(values)
  .onConflictDoUpdate({
    target: users.id,
    set: { lastLogin: sql.raw(`excluded.${users.lastLogin.name}`) },
  });
```

Generates:
```sql
insert into users ("id", "last_login")
  values (1, '2024-03-15T22:29:06.679Z')
  on conflict ("id") do update set last_login = excluded.last_login;
```

## Conditional Updates with `setWhere`

Only update if a condition is met:

```typescript
const excludedPrice = sql.raw(`excluded.${products.price.name}`);
const excludedStock = sql.raw(`excluded.${products.stock.name}`);

await db
  .insert(products)
  .values(data)
  .onConflictDoUpdate({
    target: products.id,
    set: {
      price: excludedPrice,
      stock: excludedStock,
      lastUpdated: sql.raw(`excluded.${products.lastUpdated.name}`),
    },
    setWhere: or(
      sql`${products.stock} != ${excludedStock}`,
      sql`${products.price} != ${excludedPrice}`,
    ),
  });
```

## Usage Tracking Pattern (Real Example)

For the fresh-final project's usage tracking:

```typescript
// apps/web/src/lib/usage-service.ts
import { db } from "@/db";
import { dailyUsage } from "@/db/schema";
import { sql } from "drizzle-orm";

export async function recordUsage(params: {
  userId: string;
  action: "search" | "fetch";
  costUSD: number;
}) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  await db.insert(dailyUsage)
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
}
```

## Key Takeaways

| Pattern | Syntax |
|---------|--------|
| Increment value | `sql\`${table.column} + ${value}\`` |
| Upsert target | `target: [table.col1, table.col2]` for composite |
| Set on conflict | `set: { col: sql\`${table.col} + 1\` }` |
| Decimal precision | `scale: 6` for micro-pricing (Exa API costs) |

## Sources

- [Drizzle Upsert Guide](https://orm.drizzle.team/docs/guides/upsert)
- [Drizzle Increment Guide](https://orm.drizzle.team/docs/guides/incrementing-a-value)
