# Fresh Search & Fetch API Routes Plan

## Context

This plan outlines the implementation of DeesseRPC API routes for Fresh's search and fetch functionality, powered by Exa.ai. All routes require user authentication via Better Auth.

## Overview

Fresh provides AI-optimized web search and content extraction. The API routes expose `fresh.search` and `fresh.fetch` procedures through the DeesseRPC framework, protected by Better Auth session authentication.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HTTP Route Layer                       │
│         app/(deesse)/api/[...slug]/route.ts               │
│              REST_GET / REST_POST + deesseAuth            │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                   DeesseRPC Layer                          │
│                   src/server/index.ts                     │
│         t.query / t.mutation + auth context               │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                    Fresh Core                             │
│              src/core/fresh.ts (createFresh)              │
│         search.ts + fetch.ts + errors.ts + types.ts       │
└─────────────────────┬─────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│                    Exa.ai API                              │
│                 exa-js SDK + EXA_API_KEY                  │
└─────────────────────────────────────────────────────────────┘
```

## Better Auth Context

Better Auth provides cookie-based session management:

- **Session Token**: Stored in browser cookie, referenced by `token` field in session table
- **Session Table Fields**: `id`, `token`, `userId`, `expiresAt`, `ipAddress`, `userAgent`
- **User Table Fields**: `id`, `name`, `email`, `role`, `banned`, etc.

### Server-Side Session Access

```typescript
await deesseAuth.api.getSession({
  headers: await headers()
})
```

## Implementation Steps

### 1. Update `src/core/types.ts`

Export Zod schemas for input validation:

```typescript
import { z } from 'zod';

export const SearchOptionsSchema = z.object({
  query: z.string().min(1),
  numResults: z.number().optional(),
  type: z.enum(['auto', 'fast', 'deep-lite', 'deep', 'deep-reasoning', 'instant']).optional(),
  includeDomains: z.array(z.string()).optional(),
  excludeDomains: z.array(z.string()).optional(),
  startPublishedDate: z.date().optional(),
  endPublishedDate: z.date().optional(),
  category: z.enum(['company', 'research paper', 'news', 'pdf', 'personal site', 'financial report', 'people']).optional(),
  highlights: z.object({
    query: z.string().optional(),
    maxCharacters: z.number().optional(),
  }).optional(),
  text: z.object({
    maxCharacters: z.number().optional(),
    includeHtmlTags: z.boolean().optional(),
    verbosity: z.enum(['compact', 'normal', 'verbose']).optional(),
  }).optional(),
});

export const FetchOptionsSchema = z.object({
  urls: z.union([z.string(), z.array(z.string())]),
  text: z.object({
    maxCharacters: z.number().optional(),
    includeHtmlTags: z.boolean().optional(),
  }).optional(),
  highlights: z.object({
    query: z.string().optional(),
    maxCharacters: z.number().optional(),
  }).optional(),
});

export type SearchOptionsInput = z.infer<typeof SearchOptionsSchema>;
export type FetchOptionsInput = z.infer<typeof FetchOptionsSchema>;
```

### 2. Update `src/server/index.ts`

Add Fresh procedures to the DeesseRPC router:

```typescript
import { defineContext, createAPI, createPublicAPI } from "@deessejs/server";
import { ok, err } from "@deessejs/fp";
import { z } from "zod";
import { createFresh } from "@/core";
import { SearchOptionsSchema, FetchOptionsSchema } from "@/core/types";

const { t, createAPI } = defineContext({});

// Fresh Search Procedure
const freshSearch = t.query({
  args: SearchOptionsSchema,
  handler: async (ctx, args) => {
    if (!ctx.session?.user) {
      return err({ code: "UNAUTHORIZED", message: "Authentication required" });
    }

    if (ctx.session.user.banned) {
      return err({ code: "FORBIDDEN", message: "User is banned" });
    }

    try {
      const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
      const result = await fresh.search(args);

      if (!result.ok) {
        return err({ code: "SEARCH_FAILED", message: result.error.message });
      }

      return ok(result.value);
    } catch (error) {
      return err({
        code: "INTERNAL_ERROR",
        message: error instanceof Error ? error.message : "Search failed"
      });
    }
  }
});

// Fresh Fetch Procedure
const freshFetch = t.query({
  args: FetchOptionsSchema,
  handler: async (ctx, args) => {
    if (!ctx.session?.user) {
      return err({ code: "UNAUTHORIZED", message: "Authentication required" });
    }

    if (ctx.session.user.banned) {
      return err({ code: "FORBIDDEN", message: "User is banned" });
    }

    try {
      const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
      const result = await fresh.fetch(args);

      if (!result.ok) {
        return err({ code: "FETCH_FAILED", message: result.error.message });
      }

      return ok(result.value);
    } catch (error) {
      return err({
        code: "INTERNAL_ERROR",
        message: error instanceof Error ? error.message : "Fetch failed"
      });
    }
  }
});

// Existing example procedure
const example = t.query({
  handler: async (ctx) => {
    return "heyy";
  }
});

// Router
const appRouter = t.router({
  example,
  fresh: t.router({
    search: freshSearch,
    fetch: freshFetch
  })
});

export const api = createAPI({ router: appRouter });
export const publicAPI = createPublicAPI(api);
export type AppRouter = typeof appRouter;
```

### 3. Verify Context Type for Auth

Ensure `ctx.session` and `ctx.session.user` types are properly defined. The context may need to be typed to include the Better Auth session object. This may require a plugin or explicit context typing.

### 4. Route Handler (No Changes Needed)

The existing route handler at `app/(deesse)/api/[...slug]/route.ts` already uses `deesseAuth`:

```typescript
import { deesseAuth } from "@/lib/deesse";
import { REST_GET, REST_POST } from "@deessejs/next/routes";

export const GET = REST_GET({ auth: deesseAuth });
export const POST = REST_POST({ auth: deesseAuth });
```

This already protects all procedures at the HTTP level via session cookie validation.

## Authentication Flow

```
Client                          Server
  │                               │
  │──── GET /api/fresh.search ───▶│
  │     Cookie: session=token      │
  │                               │
  │                               │── deesseAuth validates cookie
  │                               │── ctx.session populated
  │                               │── Handler checks ctx.session.user
  │                               │── createFresh() uses EXA_API_KEY
  │                               │── Exa.ai search()
  │                               │
  │◀─── { ok: true, value: {...}} ││
```

## Error Handling

| Error Code | HTTP Status | Condition |
|------------|-------------|-----------|
| `UNAUTHORIZED` | 401 | No valid session |
| `FORBIDDEN` | 403 | User banned |
| `SEARCH_FAILED` | 500 | Exa search error |
| `FETCH_FAILED` | 500 | Exa fetch error |
| `INTERNAL_ERROR` | 500 | Unexpected error |

## Files to Modify

| File | Changes |
|------|---------|
| `src/core/types.ts` | Add Zod schemas for SearchOptions and FetchOptions |
| `src/server/index.ts` | Add `freshSearch` and `freshFetch` procedures |

## Files to Verify

| File | Purpose |
|------|---------|
| `src/lib/deesse.ts` | Confirm deesseAuth session structure |
| `src/app/(deesse)/api/[...slug]/route.ts` | Confirm auth middleware setup |

## Usage Examples

### From Client Component

```typescript
import { client } from "@/server/index";

const result = await client.fresh.search({
  query: "TypeScript best practices",
  numResults: 5,
  type: "deep"
});

if (result.ok) {
  console.log(result.value.results);
}
```

### From Server Component

```typescript
import { api } from "@/server/index";

const result = await api.fresh.search({
  query: "AI startups 2024",
  type: "deep"
});
```

## Security Considerations

1. **EXA_API_KEY Protection**: The API key is server-side only, never exposed to client
2. **Session Validation**: All requests must have valid session cookie
3. **User Banned Check**: Additional check in handler prevents banned users
4. **Input Validation**: Zod schemas validate all inputs before processing
5. **Error Messages**: Internal errors not leaked to client

## Next Steps

1. Implement Zod schemas in `src/core/types.ts`
2. Update `src/server/index.ts` with procedures
3. Verify session context typing
4. Test authentication flow
5. Add integration tests for auth-protected routes
