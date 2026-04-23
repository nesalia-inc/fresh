# User Usage Tracking: Analysis and Design

## Executive Summary

This report analyzes the current architecture of the "fresh-final" project and proposes a comprehensive design for storing and managing user usage data. The system currently powers search and fetch features via the Exa.ai API, with usage data flowing through the application but not being persisted. We recommend a PostgreSQL-based usage tracking system integrated with the existing Drizzle ORM stack, using classic Next.js route handlers for all interactions.

---

## 1. Current Architecture

### 1.1 Database Schema (Drizzle ORM + PostgreSQL)

The project uses **Neon PostgreSQL** with the following existing tables:

| Table | Purpose |
|-------|---------|
| `user` | User accounts with email, name, role, banned status |
| `session` | User sessions with expiry, IP, user agent |
| `account` | OAuth provider linking (Google, GitHub) |
| `deviceCode` | Device authorization flow for CLI |
| `verification` | Email verification tokens |

### 1.2 Usage Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Web UI     │     │  CLI        │     │  API Client │
│  /search    │     │  fresh search│    │  (api.ts)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                   ┌─────────────┐
                   │  REST API   │
                   │  /api/search│
                   │  /api/fetch │
                   └──────┬──────┘
                          │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Search     │     │  Fetch      │     │  Usage      │
│  Handler    │     │  Handler    │     │  Recording  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                   ┌─────────────┐
                   │  Core Layer │
                   │  fresh.ts   │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Exa.ai API │
                   │  (exa-js)   │
                   └─────────────┘
```

### 1.3 Exa.ai API Response Data

Every Exa API call returns cost information:

```typescript
// From apps/web/src/core/search.ts
{
  results: SearchResult[],
  requestId: string,
  autoDate: string,
  costDollars: {
    stDollars: number,    // Search token cost
    totalCost: number     // Total dollar cost
  },
  statuses: { [url: string]: "success" | "error" | "notFound" | "unavailable" }
}
```

---

## 2. Available Tracking Points

### 2.1 At REST API Route Handlers (Primary)

**File:** `apps/web/src/app/api/search/route.ts`

```typescript
// Current flow - no usage recording
export async function POST(request: Request) {
  const session = await deesseAuth.api.getSession()
  const parsed = await SearchOptionsSchema.safeParseAsync(await request.json())
  const fresh = new Fresh({ apiKey: EXA_API_KEY })
  const start = Date.now()
  const result = await fresh.search(parsed.data)
  const durationMs = Date.now() - start

  // Track here: extract costDollars from result.value, save to DB
  return Response.json(result.value)
}
```

**File:** `apps/web/src/app/api/fetch/route.ts`

```typescript
// Current flow - no usage recording
export async function POST(request: Request) {
  const session = await deesseAuth.api.getSession()
  const parsed = await FetchOptionsSchema.safeParseAsync(await request.json())
  const fresh = new Fresh({ apiKey: EXA_API_KEY })
  const start = Date.now()
  const result = await fresh.fetch(parsed.data)
  const durationMs = Date.now() - start

  // Track here: extract costDollars from result.value, save to DB
  return Response.json(result.value)
}
```

**Tracking opportunity:** After extracting cost data from the Exa response and before returning to the client, record the usage.

---

## 3. Proposed Schema Design

### 3.1 Daily Aggregates Table (Primary - for Billing)

```typescript
// apps/web/src/db/schema/usage-schema.ts

import { pgTable, text, timestamp, decimal, integer, index } from "drizzle-orm/pg-core";
import { user } from "./auth-schema";

export const dailyUsage = pgTable("daily_usage", {
  id: integer("id").primaryKey().autoIncrement(),

  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),

  date: timestamp("date").notNull(),  // Day granularity (set to midnight)

  // Counts
  searchCount: integer("search_count").notNull().default(0),
  fetchCount: integer("fetch_count").notNull().default(0),

  // Costs (6 decimal places for micro-pricing from Exa)
  totalCostUSD: decimal("total_cost_usd", {
    precision: 10,
    scale: 6
  }).notNull().default("0"),

  updatedAt: timestamp("updated_at")
    .defaultNow()
    .$onUpdate(() => new Date()),
}, (table) => [
  // Composite unique index for upsert target
  index("daily_usage_user_date_idx").on(table.userId, table.date),
])
```

> **Key Pattern:** `onConflictDoUpdate` on `(userId, date)` with increment expressions:
> ```typescript
> await db.insert(dailyUsage)
>   .values({ userId, date: today, searchCount: 1, totalCostUSD: costUSD })
>   .onConflictDoUpdate({
>     target: [dailyUsage.userId, dailyUsage.date],
>     set: {
>       searchCount: sql`${dailyUsage.searchCount} + 1`,
>       totalCostUSD: sql`${dailyUsage.totalCostUSD} + ${costUSD}`,
>     },
>   });
> ```

### 3.2 Rate Limits Table (for Quotas)

```typescript
export const userQuota = pgTable("user_quota", {
  id: integer("id").primaryKey().autoIncrement(),

  userId: text("user_id")
    .notNull()
    .unique()
    .references(() => user.id, { onDelete: "cascade" }),

  // Tier-based limits
  tier: text("tier", {
    enum: ["free", "pro", "enterprise"]
  }).notNull().default("free"),

  // Monthly limits
  monthlySearchLimit: integer("monthly_search_limit").notNull().default(100),
  monthlyFetchLimit: integer("monthly_fetch_limit").notNull().default(50),
  monthlyCostLimitUSD: decimal("monthly_cost_limit_usd", {
    precision: 10,
    scale: 2
  }).notNull().default("10.00"),

  // Current month usage (reset monthly)
  currentMonthSearches: integer("current_month_searches").notNull().default(0),
  currentMonthFetches: integer("current_month_fetches").notNull().default(0),
  currentMonthCostUSD: decimal("current_month_cost_usd", {
    precision: 10,
    scale: 6
  }).notNull().default("0"),

  periodStart: timestamp("period_start").defaultNow().notNull(),

  updatedAt: timestamp("updated_at")
    .defaultNow()
    .$onUpdate(() => new Date()),
})
```

---

## 4. Implementation Strategies

### 4.1 Strategy A: Service Layer with Route Handlers (Recommended)

**Pros:** Full control over recording, integrated with existing route pattern, easy to test
**Cons:** Must update each route handler

```typescript
// apps/web/src/lib/usage-service.ts
import { db } from "@/db";
import { dailyUsage } from "@/db/schema";
import { eq, sql } from "drizzle-orm";

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

> **Note:** Detailed per-request records can be added separately if needed for analytics. For billing, the daily aggregate upsert pattern above is sufficient and more efficient.

**Route Handler Integration:**

```typescript
// apps/web/src/app/api/search/route.ts
import { deesseAuth } from "@/lib/deesse";
import { recordUsage } from "@/lib/usage-service";
import { SearchOptionsSchema } from "@/core/search";
import { Fresh } from "@/core/fresh";

export async function POST(request: Request) {
  try {
    const session = await deesseAuth.api.getSession();
    if (!session) {
      return Response.json({ error: "Unauthorized" }, { status: 401 });
    }

    const parsed = await SearchOptionsSchema.safeParseAsync(await request.json());
    if (!parsed.success) {
      return Response.json({ error: parsed.error.flatten() }, { status: 400 });
    }

    const fresh = new Fresh({ apiKey: process.env.EXA_API_KEY! });
    const result = await fresh.search(parsed.data);

    if (result.isOk) {
      const costUSD = result.value.costDollars?.totalCost ?? 0;

      // Record usage asynchronously (non-blocking)
      recordUsage({
        userId: session.user.id,
        action: "search",
        costUSD,
      }).catch(console.error); // Don't block response on recording failure
    }

    return Response.json(result.value);
  } catch (error) {
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
```

### 4.2 Strategy B: Async Queue (for High Volume)

**Pros:** Non-blocking, handles traffic spikes, resilient to DB overload
**Cons:** Additional infrastructure (Redis/queue), eventual consistency

```typescript
// apps/web/src/lib/usage-queue.ts
import { Queue } from "bullmq";

const usageQueue = new Queue("usage-recording", {
  connection: redisConnection,
});

export async function enqueueUsageRecord(data: UsageRecordData) {
  await usageQueue.add("record", data, {
    attempts: 3,
    backoff: { type: "exponential", delay: 1000 },
  });
}
```

### 4.3 Strategy C: Route Middleware (Next.js)

**Pros:** Centralized, can intercept all matching routes
**Cons:** Limited to specific route patterns, more complex setup

```typescript
// apps/web/src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  if (path.startsWith("/api/search") || path.startsWith("/api/fetch")) {
    // Add usage recording logic via queue
    // This runs before the route handler
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/api/search", "/api/fetch"],
};
```

---

## 5. Query Patterns for Usage Display

Usage is stored as daily aggregates in `dailyUsage`. All queries read from that table directly.

### 5.1 User's Current Month Usage

```typescript
// apps/web/src/lib/queries.ts
import { db } from "@/db";
import { dailyUsage } from "@/db/schema";
import { and, eq, gte, sql } from "drizzle-orm";

export async function getUserCurrentMonthUsage(userId: string) {
  const periodStart = getStartOfMonth();

  const [usage] = await db
    .select({
      totalSearches: sql<number>`COALESCE(SUM(${dailyUsage.searchCount}), 0)`,
      totalFetches: sql<number>`COALESCE(SUM(${dailyUsage.fetchCount}), 0)`,
      totalCost: sql<number>`COALESCE(SUM(CAST(${dailyUsage.totalCostUSD} AS numeric)), 0)`,
    })
    .from(dailyUsage)
    .where(and(
      eq(dailyUsage.userId, userId),
      gte(dailyUsage.date, periodStart),
    ));

  return {
    searches: Number(usage.totalSearches),
    fetches: Number(usage.totalFetches),
    costUSD: Number(usage.totalCost),
    periodStart,
  };
}

function getStartOfMonth(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1);
}
```

### 5.2 Usage History with Pagination

```typescript
export async function getUserUsageHistory(
  userId: string,
  page: number = 1,
  limit: number = 20
) {
  const offset = (page - 1) * limit;

  const records = await db
    .select()
    .from(dailyUsage)
    .where(eq(dailyUsage.userId, userId))
    .orderBy(dailyUsage.date)
    .limit(limit)
    .offset(offset);

  const [{ count }] = await db
    .select({ count: sql<number>`COUNT(*)` })
    .from(dailyUsage)
    .where(eq(dailyUsage.userId, userId));

  return {
    records,
    pagination: {
      page,
      limit,
      total: Number(count),
      totalPages: Math.ceil(Number(count) / limit),
    },
  };
}
```

### 5.3 Daily Usage Chart Data

```typescript
export async function getDailyUsageForPeriod(userId: string, days: number = 30) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const daily = await db
    .select({
      date: dailyUsage.date,
      searches: dailyUsage.searchCount,
      fetches: dailyUsage.fetchCount,
      cost: sql<number>`CAST(${dailyUsage.totalCostUSD} AS numeric)`,
    })
    .from(dailyUsage)
    .where(and(
      eq(dailyUsage.userId, userId),
      gte(dailyUsage.date, startDate),
    ))
    .orderBy(dailyUsage.date);

  return daily;
}
```

### 5.4 Get Quota Status

```typescript
import { userQuota } from "@/db/schema";

export async function getQuotaStatus(userId: string) {
  const quota = await db.query.userQuota.findFirst({
    where: eq(userQuota.userId, userId),
  });

  if (!quota) {
    return {
      tier: "free",
      searches: { used: 0, limit: 100 },
      fetches: { used: 0, limit: 50 },
      cost: { used: 0, limit: 10 },
    };
  }

  return {
    tier: quota.tier,
    searches: {
      used: quota.currentMonthSearches,
      limit: quota.monthlySearchLimit,
    },
    fetches: {
      used: quota.currentMonthFetches,
      limit: quota.monthlyFetchLimit,
    },
    cost: {
      used: Number(quota.currentMonthCostUSD),
      limit: Number(quota.monthlyCostLimitUSD),
    },
  };
}
```

---

## 6. Rate Limiting Integration

### 6.1 Quota Check Utility

```typescript
// apps/web/src/lib/quota-service.ts
import { db } from "@/db";
import { userQuota } from "@/db/schema";
import { eq } from "drizzle-orm";
import { RateLimitError } from "@/core/errors";

export async function checkQuota(
  userId: string,
  action: "search" | "fetch",
  costUSD: number
) {
  const quota = await db.query.userQuota.findFirst({
    where: eq(userQuota.userId, userId),
  });

  if (!quota) {
    // Create default free tier quota
    await db.insert(userQuota).values({ userId });
    return checkQuota(userId, action, costUSD);
  }

  const periodStart = new Date(quota.periodStart);
  const now = new Date();

  // Reset if new month
  if (now.getMonth() !== periodStart.getMonth()) {
    await db.update(userQuota)
      .set({
        currentMonthSearches: 0,
        currentMonthFetches: 0,
        currentMonthCostUSD: "0",
        periodStart: now,
      })
      .where(eq(userQuota.userId, userId));
    return checkQuota(userId, action, costUSD);
  }

  const limit = action === "search" ? quota.monthlySearchLimit : quota.monthlyFetchLimit;
  const current = action === "search" ? quota.currentMonthSearches : quota.currentMonthFetches;
  const newCost = Number(quota.currentMonthCostUSD) + costUSD;

  if (current >= limit) {
    throw new RateLimitError(`Monthly ${action} limit reached (${limit})`);
  }

  if (newCost > Number(quota.monthlyCostLimitUSD)) {
    throw new RateLimitError(`Monthly cost limit of $${quota.monthlyCostLimitUSD} exceeded`);
  }

  return true;
}
```

### 6.2 Update Quota After Request

```typescript
export async function incrementQuota(
  userId: string,
  action: "search" | "fetch",
  costUSD: number
) {
  await db.update(userQuota)
    .set({
      ...(action === "search"
        ? { currentMonthSearches: sql`${userQuota.currentMonthSearches} + 1` }
        : { currentMonthFetches: sql`${userQuota.currentMonthFetches} + 1` }
      ),
      currentMonthCostUSD: sql`${userQuota.currentMonthCostUSD} + ${costUSD}`,
    })
    .where(eq(userQuota.userId, userId));
}
```

### 6.3 Route Handler with Quota Check

```typescript
// apps/web/src/app/api/search/route.ts
import { deesseAuth } from "@/lib/deesse";
import { recordUsage, checkQuota, incrementQuota } from "@/lib/usage-service";
import { SearchOptionsSchema } from "@/core/search";
import { Fresh } from "@/core/fresh";

export async function POST(request: Request) {
  try {
    const session = await deesseAuth.api.getSession();
    if (!session) {
      return Response.json({ error: "Unauthorized" }, { status: 401 });
    }

    const parsed = await SearchOptionsSchema.safeParseAsync(await request.json());
    if (!parsed.success) {
      return Response.json({ error: parsed.error.flatten() }, { status: 400 });
    }

    // Estimate cost (use previous average or max estimate)
    const estimatedCost = 0.001; // $0.001 per search estimate

    // Check quota before making API call
    await checkQuota(session.user.id, "search", estimatedCost);

    const fresh = new Fresh({ apiKey: process.env.EXA_API_KEY! });
    const start = Date.now();
    const result = await fresh.search(parsed.data);
    const durationMs = Date.now() - start;

    if (result.isOk) {
      const costUSD = result.value.costDollars?.totalCost ?? 0;

      // Update quota after successful request
      await incrementQuota(session.user.id, "search", costUSD);

      // Record usage (non-blocking)
      recordUsage({
        userId: session.user.id,
        action: "search",
        costUSD,
        durationMs,
        status: "success",
        metadata: {
          searchType: parsed.data.type,
          numResults: parsed.data.numResults,
        },
      }).catch(console.error);
    }

    return Response.json(result.value);
  } catch (error) {
    if (error instanceof RateLimitError) {
      return Response.json({ error: error.message }, { status: 429 });
    }
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
```

---

## 7. File Structure

```
apps/web/src/
├── db/
│   └── schema/
│       ├── index.ts
│       ├── auth-schema.ts       # Existing: user, session, account
│       └── usage-schema.ts     # NEW: dailyUsage, userQuota
├── lib/
│   ├── usage-service.ts        # NEW: recordUsage, incrementQuota
│   ├── quota-service.ts        # NEW: checkQuota
│   └── queries.ts              # NEW: usage query functions
├── core/
│   └── errors.ts               # Existing: RateLimitError
├── app/
│   └── (frontend)/(protected)/home/
│       ├── usage/
│       │   └── page.tsx        # NEW: usage dashboard
│       └── billing/
│           └── page.tsx         # NEW: billing page
└── app/api/
    ├── search/
    │   └── route.ts           # MODIFIED: add usage recording
    └── fetch/
        └── route.ts           # MODIFIED: add usage recording
```

---

## 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage granularity | Daily aggregates only | Efficient for billing, no per-request overhead |
| Cost precision | 6 decimal places | Exa API costs can be very small ($0.000123) |
| Quota reset | Monthly | Standard SaaS billing model |
| Indexing | Composite index on (userId, date) | Enables fast upsert and queries |
| Rate limit approach | Pre-check before request | Fail fast, don't waste Exa API quota |
| Recording | Async/non-blocking | Don't add latency to API responses |

---

## 9. Backward Compatibility

The usage tracking system should be deployed in phases:

1. **Phase 1:** Record-only (no rate limiting) - all requests proceed
2. **Phase 2:** Quota warnings in response headers (X-RateLimit-Remaining)
3. **Phase 3:** Active rate limiting for free tier
4. **Phase 4:** Billing integration with Stripe/custom billing

This approach ensures existing users are not disrupted and the system can be validated incrementally.

---

## 10. Stripe Integration (Phase 4)

The [better-auth Stripe plugin](https://better-auth.com/docs/plugins/stripe) can be integrated in Phase 4 to provide subscription billing.

### What Stripe Plugin Provides

| Feature | Description |
|---------|-------------|
| Stripe Customer creation | Auto-created on user sign-up |
| Subscription management | Plans, pricing, lifecycle events |
| Webhook handling | Secure signature verification |
| Trial abuse prevention | One trial per user across all plans |
| **Plan limits** | `limits` object per plan (our key interest) |

### Plan Limits in Stripe Plugin

```typescript
subscription: {
  enabled: true,
  plans: [
    {
      name: "basic",
      priceId: "price_1234567890",
      limits: {
        monthlySearchLimit: 100,
        monthlyFetchLimit: 50,
        monthlyCostLimitUSD: 10.00
      }
    },
    {
      name: "pro",
      priceId: "price_0987654321",
      limits: {
        monthlySearchLimit: 1000,
        monthlyFetchLimit: 500,
        monthlyCostLimitUSD: 100.00
      },
      freeTrial: { days: 14 }
    }
  ]
}
```

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Stripe Plugin                            │
│  - Subscription lifecycle (create, update, cancel)         │
│  - Plan definitions with limits                            │
│  - Webhook events                                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Webhook Handler (subscription.created/updated/deleted)      │
│                                                             │
│  On subscription event:                                      │
│    1. Extract plan limits from Stripe                        │
│    2. Update userQuota with new limits + tier                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Our Usage Tracking System (Phases 1-3)                       │
│                                                             │
│  - dailyUsage: usage aggregates                              │
│  - userQuota: current month usage + limits from Stripe       │
│  - checkQuota(): enforces limits (from Stripe plan)          │
└─────────────────────────────────────────────────────────────┘
```

### Gap: What Stripe Plugin Doesn't Provide

| Missing | Implication |
|---------|-------------|
| Real-time usage tracking | We still track search/fetch counts |
| Cost accumulation from Exa | We calculate from Exa response |
| Monthly reset logic | Our `periodStart` handles this |
| Rate limit enforcement | Our `checkQuota()` enforces before API call |

### Quota Initialization from Stripe

When a Stripe subscription is created/updated, sync to `userQuota`:

```typescript
// apps/web/src/lib/stripe-sync.ts
import { db } from "@/db";
import { userQuota } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function syncQuotaFromStripe(params: {
  userId: string;
  tier: "free" | "pro" | "enterprise";
  monthlySearchLimit: number;
  monthlyFetchLimit: number;
  monthlyCostLimitUSD: number;
}) {
  await db.insert(userQuota)
    .values({
      userId: params.userId,
      tier: params.tier,
      monthlySearchLimit: params.monthlySearchLimit,
      monthlyFetchLimit: params.monthlyFetchLimit,
      monthlyCostLimitUSD: params.monthlyCostLimitUSD.toString(),
    })
    .onConflictDoUpdate({
      target: userQuota.userId,
      set: {
        tier: params.tier,
        monthlySearchLimit: params.monthlySearchLimit,
        monthlyFetchLimit: params.monthlyFetchLimit,
        monthlyCostLimitUSD: params.monthlyCostLimitUSD.toString(),
        currentMonthSearches: 0,
        currentMonthFetches: 0,
        currentMonthCostUSD: "0",
        periodStart: new Date(),
      },
    });
}
```

### Deployment Order

1. **Phase 1-3:** Implement usage tracking + quota without Stripe
2. **Phase 4:** Add Stripe plugin, connect plan limits to `userQuota`
3. **Phase 5:** Use Stripe webhooks to keep `userQuota` in sync

---

## 11. Conclusion

The current architecture provides clear entry points for usage tracking through classic Next.js REST API route handlers at `apps/web/src/app/api/search/route.ts` and `apps/web/src/app/api/fetch/route.ts`. These handlers already extract cost data from Exa responses but don't persist it.

The recommended approach is **Strategy A (Service Layer)** which:
- Creates a `usage-service.ts` with `recordUsage()` and `incrementQuota()` functions
- Integrates into existing route handlers with minimal changes
- Records usage asynchronously to avoid adding latency to responses
- Uses `onConflictDoUpdate` for efficient daily aggregate upserts

The schema design supports multi-tenant SaaS with user-specific quotas and rate limiting, following the existing Drizzle ORM patterns in the codebase.

---

## 12. Related Documentation

For detailed Drizzle ORM patterns used in this design:

- [Upsert & Increment Patterns](../../learnings/drizzle/upsert-increment.md) - `onConflictDoUpdate`, increment expressions
- [Batch & Transactions](../../learnings/drizzle/batch-transactions.md) - Atomic operations, transaction patterns
- [Schema Design](../../learnings/drizzle/schema-design.md) - Naming conventions, indexes, column types
- [Query Optimization](../../learnings/drizzle/query-optimization.md) - Prepared statements, pagination
- [Connection & Errors](../../learnings/drizzle/connection-errors.md) - Error codes, pool configuration
