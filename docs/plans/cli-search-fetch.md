# Fresh Search & Fetch CLI Implementation Plan

## Chosen Approach: Simple HTTP REST API

Instead of using DeesseRPC (which has complex routing issues), we will create simple HTTP REST endpoints at `/api/search` and `/api/fetch`.

**Advantages:**
- Simple to understand and debug
- Works with any HTTP client (curl, fetch, etc.)
- No dependency on DeesseRPC internals
- Easy to test with curl

**Trade-offs:**
- Lose type-safety between server and client
- Manual input validation required

---

## Problem Analysis

### Problem 1: No Existing REST Endpoints

Currently there are no `/api/search` or `/api/fetch` routes. Need to create them.

### Problem 2: Authentication on API Routes

Need to validate bearer tokens on these new routes. The bearer plugin is already enabled, so we can use `deesseAuth.api.getSession()` with request headers.

### Problem 3: CLI Command Structure

- `@nesalia/fresh` CLI with `auth` subcommands
- Need to add `search` and `fetch` commands

---

## Implementation Plan

### Phase 1: Create REST API Routes

**New File: `apps/web/src/app/api/search/route.ts`**
```typescript
import { NextRequest } from "next/server";
import { deesseAuth } from "@/lib/deesse";
import { createFresh } from "@/core";
import { SearchOptionsSchema } from "@/core/types";

export async function POST(request: NextRequest) {
  // 1. Validate authentication
  const session = await deesseAuth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return Response.json(
      { error: "Unauthorized", message: "Not authenticated" },
      { status: 401 }
    );
  }

  // 2. Parse and validate request body
  const body = await request.json();
  const parsed = SearchOptionsSchema.safeParse(body);

  if (!parsed.success) {
    return Response.json(
      { error: "Validation Error", message: parsed.error.message },
      { status: 400 }
    );
  }

  // 3. Execute search
  try {
    const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
    const result = await fresh.search(parsed.data);

    if (!result.ok) {
      return Response.json(
        { error: "Search Failed", message: result.error.message },
        { status: 500 }
      );
    }

    return Response.json(result.value);
  } catch (error) {
    return Response.json(
      { error: "Internal Error", message: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
```

**New File: `apps/web/src/app/api/fetch/route.ts`**
```typescript
import { NextRequest } from "next/server";
import { deesseAuth } from "@/lib/deesse";
import { createFresh } from "@/core";
import { FetchOptionsSchema } from "@/core/types";

export async function POST(request: NextRequest) {
  // 1. Validate authentication
  const session = await deesseAuth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return Response.json(
      { error: "Unauthorized", message: "Not authenticated" },
      { status: 401 }
    );
  }

  // 2. Parse and validate request body
  const body = await request.json();
  const parsed = FetchOptionsSchema.safeParse(body);

  if (!parsed.success) {
    return Response.json(
      { error: "Validation Error", message: parsed.error.message },
      { status: 400 }
    );
  }

  // 3. Execute fetch
  try {
    const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });
    const result = await fresh.fetch(parsed.data);

    if (!result.ok) {
      return Response.json(
        { error: "Fetch Failed", message: result.error.message },
        { status: 500 }
      );
    }

    return Response.json(result.value);
  } catch (error) {
    return Response.json(
      { error: "Internal Error", message: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
```

---

### Phase 2: CLI Commands

**New File: `apps/cli/src/lib/api.ts`**
```typescript
import { getCredential } from "./storage.js";

const API_BASE = process.env.FRESH_API_URL || "https://fresh.nesalia.com";

export interface SearchOptions {
  query: string;
  limit?: number;
  type?: "auto" | "article" | "news";
}

export interface FetchOptions {
  url: string;
  prompt?: string;
}

export interface SearchResult {
  results: Array<{
    title: string;
    url: string;
    score: number;
    snippet: string;
  }>;
}

export interface FetchResult {
  title: string;
  content: string;
  author?: string;
  publishedDate?: string;
}

export class APIError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const cred = await getCredential();
  if (!cred) {
    throw new APIError("Not authenticated. Run 'fresh auth login' first.", "UNAUTHENTICATED", 401);
  }
  return {
    Authorization: `Bearer ${cred.accessToken}`,
  };
}

export async function search(options: SearchOptions): Promise<SearchResult> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Unknown error" }));
    throw new APIError(error.message || "Search failed", error.code || "SEARCH_FAILED", response.status);
  }

  return response.json();
}

export async function fetchUrl(options: FetchOptions): Promise<FetchResult> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/fetch`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Unknown error" }));
    throw new APIError(error.message || "Fetch failed", error.code || "FETCH_FAILED", response.status);
  }

  return response.json();
}
```

**New File: `apps/cli/src/commands/search.ts`**
```typescript
import { Command } from "commander";
import { search, APIError } from "../lib/api.js";

export const searchCmd = new Command()
  .name("search")
  .description("Search the web using Exa.ai")
  .option("-q, --query <text>", "Search query", { required: true })
  .option("-l, --limit <number>", "Maximum number of results", { default: 10 })
  .option("-t, --type <type>", "Type of search (auto, article, news)", { default: "auto" })
  .action(async (options) => {
    try {
      console.log("\n🔍 Searching...\n");

      const result = await search({
        query: options.query,
        limit: parseInt(options.limit, 10),
        type: options.type,
      });

      if (!result.results || result.results.length === 0) {
        console.log("No results found.\n");
        return;
      }

      console.log(`Found ${result.results.length} results:\n`);

      result.results.forEach((r, i) => {
        console.log(`${i + 1}. ${r.title}`);
        console.log(`   URL: ${r.url}`);
        console.log(`   Score: ${(r.score * 100).toFixed(1)}%`);
        if (r.snippet) {
          console.log(`   ${r.snippet.substring(0, 200)}${r.snippet.length > 200 ? "..." : ""}`);
        }
        console.log();
      });
    } catch (error) {
      if (error instanceof APIError) {
        console.error(`\n❌ Search failed: ${error.message}`);
        if (error.statusCode === 401) {
          console.error("   Run 'fresh auth login' to authenticate.\n");
        } else {
          console.error();
        }
      } else {
        console.error(`\n❌ Search failed: ${error instanceof Error ? error.message : "Unknown error"}\n`);
      }
      process.exit(1);
    }
  });
```

**New File: `apps/cli/src/commands/fetch.ts`**
```typescript
import { Command } from "commander";
import { fetchUrl, APIError } from "../lib/api.js";

export const fetchCmd = new Command()
  .name("fetch")
  .description("Fetch and extract content from a URL")
  .argument("<url>", "URL to fetch")
  .option("-p, --prompt <text>", "Prompt for content extraction")
  .action(async (url, options) => {
    try {
      console.log(`\n📄 Fetching ${url}...\n`);

      const result = await fetchUrl({
        url,
        prompt: options.prompt,
      });

      console.log(`📰 ${result.title}`);
      if (result.author) {
        console.log(`👤 Author: ${result.author}`);
      }
      if (result.publishedDate) {
        console.log(`📅 Published: ${result.publishedDate}`);
      }
      console.log("\n" + "─".repeat(50) + "\n");
      console.log(result.content);
      console.log("\n" + "─".repeat(50) + "\n");
    } catch (error) {
      if (error instanceof APIError) {
        console.error(`\n❌ Fetch failed: ${error.message}`);
        if (error.statusCode === 401) {
          console.error("   Run 'fresh auth login' to authenticate.\n");
        } else {
          console.error();
        }
      } else {
        console.error(`\n❌ Fetch failed: ${error instanceof Error ? error.message : "Unknown error"}\n`);
      }
      process.exit(1);
    }
  });
```

**Update: `apps/cli/src/index.ts`**
```typescript
import { searchCmd } from "./commands/search.js";
import { fetchCmd } from "./commands/fetch.js";

program
  .addCommand(searchCmd)
  .addCommand(fetchCmd);
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `apps/web/src/app/api/search/route.ts` | Create | REST endpoint for search |
| `apps/web/src/app/api/fetch/route.ts` | Create | REST endpoint for fetch |
| `apps/cli/src/lib/api.ts` | Create | Shared API client with auth |
| `apps/cli/src/commands/search.ts` | Create | Search command |
| `apps/cli/src/commands/fetch.ts` | Create | Fetch command |
| `apps/cli/src/index.ts` | Modify | Register new commands |
| `apps/cli/package.json` | Modify | Bump version |

---

## Testing Checklist

### Server Routes
```bash
# Get a token first
fresh auth login

# Test search endpoint
curl -X POST https://fresh.nesalia.com/api/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query":"AI news","limit":5}'

# Test fetch endpoint
curl -X POST https://fresh.nesalia.com/api/fetch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"url":"https://example.com"}'
```

### CLI Commands
```bash
# Test search
fresh search --query "AI news" --limit 5

# Test fetch
fresh fetch https://example.com
```

---

## Security Considerations

1. **Token Storage:** ✅ Access tokens in OS keychain via keytar
2. **Bearer Token Validation:** ✅ Using better-auth's `getSession()` on each request
3. **Input Validation:** ✅ Using Zod schemas (SearchOptionsSchema, FetchOptionsSchema)
4. **Error Messages:** ✅ Don't expose internal details in production

---

## Environment Variables

| Variable | CLI | Server | Description |
|----------|-----|--------|-------------|
| `FRESH_API_URL` | Yes | No | API base URL (default: https://fresh.nesalia.com) |
| `EXA_API_KEY` | No | Yes | Exa.ai API key for search/fetch |
| `DEESSE_SECRET` | No | Yes | Secret for DeesseJS |
| `DATABASE_URL` | No | Yes | PostgreSQL database connection string |
| `NEXT_PUBLIC_BASE_URL` | No | Yes | Base URL for the application |
