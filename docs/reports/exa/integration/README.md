# Fresh + Exa.ai Integration Report

## Context

Fresh is a web search and content extraction tool powered by Exa.ai. This report analyzes the integration of Exa's TypeScript SDK (`exa-js`) into the Fresh project at `packages/core`, implementing only `search` and `fetch` (content retrieval) features.

## Project State

| Component | Status |
|-----------|--------|
| `apps/web` | Next.js 16 + DeesseJS (auth only) |
| `apps/cli` | Placeholder (empty) |
| `packages/` | Empty (new) |
| `docs/features/` | Contains full specs for search, fetch, ask, research |

## Goals

- Implement `search` and `fetch` only (not ask/research)
- No streaming (operations are fast)
- Use Exa.ai TypeScript SDK directly (`exa-js`)
- Create reusable `packages/core`

## Exa.ai SDK Overview

### Installation

```bash
npm install exa-js
```

### Authentication

```typescript
const exa = new Exa(); // Reads EXA_API_KEY from environment
// or
const exa = new Exa("your-api-key");
```

### Core Methods

| Method | Purpose |
|--------|---------|
| `exa.search(query, options)` | Web search |
| `exa.searchAndContents(query, options)` | Search + fetch in one call |
| `exa.getContents(urls, options)` | Fetch content from URLs |
| `exa.findSimilar(url, options)` | Find similar pages |
| `exa.answer(query, options)` | Synthesized answers |

### Search Options

```typescript
interface RegularSearchOptions {
  type?: 'auto' | 'fast' | 'deep-lite' | 'deep' | 'deep-reasoning' | 'instant';
  numResults?: number;
  includeDomains?: string[];
  excludeDomains?: string[];
  startPublishedDate?: Date;
  endPublishedDate?: Date;
  category?: 'company' | 'research paper' | 'news' | 'pdf' | 'personal site' | 'financial report' | 'people';
  contents?: ContentsOptions;
  highlights?: HighlightsOptions;
  text?: TextOptions;
}
```

### Contents Options

```typescript
interface ContentsOptions {
  text?: {
    maxCharacters?: number;
    includeHtmlTags?: boolean;
    verbosity?: 'high' | 'medium' | 'low';
    includeSections?: SectionTag[];
    excludeSections?: SectionTag[];
  };
  highlights?: {
    query: string;
    maxCharacters?: number;
  };
  summary?: {
    query: string;
    schema?: Record | ZodSchema;
  };
}
```

### Response Types

```typescript
interface SearchResult {
  title: string;
  url: string;
  id: string;
  publishedDate?: string;
  author?: string;
  score?: number;
  image?: string;
  favicon?: string;
  text?: string;
  highlights?: string[];
  highlightScores?: number[];
  summary?: string;
  entities?: Entity[];
}

interface SearchResponse {
  results: SearchResult[];
  requestId: string;
  autopromptString?: string;
  costDollars?: {
    stDollars: number;
    totalCost: number;
  };
  statuses?: Array<{
    code: 'success' | 'error' | 'notFound' | 'unavailable';
    url: string;
  }>;
  output?: {
    content: string;
    grounding: Array<{
      field: string;
      citations: Array<{ url: string; title: string }>;
      confidence: 'low' | 'medium' | 'high';
    }>;
  };
}
```

## Proposed Architecture

### Directory Structure

```
packages/
└── core/
    ├── src/
    │   ├── index.ts           # Public exports (createFresh, types)
    │   ├── fresh.ts           # createFresh() factory function
    │   ├── search.ts          # search() implementation
    │   ├── fetch.ts           # fetch() implementation
    │   ├── types.ts           # TypeScript types
    │   └── errors.ts          # Error factories (not classes)
    ├── package.json
    ├── tsconfig.json
    └── README.md
```

> **Note:** This project follows a [no-classes rule](../../rules/no-classes.md). All APIs use factory functions instead of classes.

### Package.json

```json
{
  "name": "@fresh/core",
  "version": "0.1.0",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  },
  "dependencies": {
    "exa-js": "latest"
  },
  "peerDependencies": {
    "@deessejs/fp": ">=3.0.0",
    "zod": ">=3.0.0"
  }
}
```

> **Note:** Uses `@deessejs/fp` for functional error handling patterns (Result, Try, error factories).

### API Design

```typescript
import { pipe, isOk, isErr, getOrElse, tap, map } from '@deessejs/fp';
import { createFresh } from '@fresh/core';

const fresh = createFresh({
  apiKey: process.env.EXA_API_KEY
});

// Search - returns AsyncResult
const searchResult = await fresh.search({
  query: 'latest AI developments',
  numResults: 10,
  type: 'auto'
});

// Handle with tap for logging (tap passes Result through unchanged)
const results = pipe(
  searchResult,
  tap(r => isErr(r) ? console.error(r.error.message) : null)
);

// Fetch - returns AsyncResult
const fetchResult = await fresh.fetch({
  urls: ['https://example.com/article'],
  text: { maxCharacters: 1000 },
  highlights: { query: 'AI', maxCharacters: 200 }
});

// Or use getOrElse for default value
const data = getOrElse(fetchResult, {
  results: [],
  requestId: '',
  costDollars: { stDollars: 0, totalCost: 0 },
  statuses: []
});
```

## Error Handling

Following the [deesse-fp error rules](../../../.claude/skills/deesse-fp/rules/error-handling.md), errors travel through `Result`, not thrown.

### Error Types

| Code | Description |
|------|-------------|
| `INVALID_QUERY` | Query is empty or invalid |
| `INVALID_URL` | URL format is invalid or missing protocol |
| `SEARCH_ERROR` | Search operation failed |
| `FETCH_ERROR` | Failed to fetch URL content |
| `TIMEOUT` | Request exceeded timeout limit |
| `PARSE_ERROR` | Failed to parse content |
| `RATE_LIMITED` | Rate limit exceeded |
| `UNAUTHORIZED` | Invalid or missing API key |

### Error Factories (using @deessejs/fp)

```typescript
import { error } from '@deessejs/fp';
import { z } from 'zod';

// Structured errors using deesse-fp error() factory
const SearchError = error({
  name: 'SearchError',
  schema: z.object({
    query: z.string(),
    reason: z.string().optional(),
  }),
  message: (args) => args.reason
    ? `Search failed for "${args.query}": ${args.reason}`
    : `Search failed for "${args.query}"`
});

const FetchError = error({
  name: 'FetchError',
  schema: z.object({
    url: z.string(),
    reason: z.string().optional(),
  }),
  message: (args) => args.reason
    ? `Fetch failed for "${args.url}": ${args.reason}`
    : `Fetch failed for "${args.url}"`
});

const RateLimitError = error({
  name: 'RateLimitError',
  schema: z.object({
    retryAfter: z.number().optional(),
  }),
  message: (args) => args.retryAfter
    ? `Rate limited. Retry after ${args.retryAfter}s`
    : 'Rate limited'
});
```

### Error Usage Pattern

```typescript
import { pipe, ok, fromPromise, map, mapErr } from '@deessejs/fp';

// Errors return in Result, not thrown - using pipe for composition
const search = (query: string): AsyncResult<SearchResponse, ReturnType<typeof SearchError>> =>
  pipe(
    exa.search(query),
    fromPromise,
    map(response => response),
    mapErr(e =>
      SearchError({ query, reason: e.message })
        .addNotes('Exa search operation failed')
    )
  );
```

### Error Enrichment with tap

```typescript
import { pipe, tap, mapErr, isErr } from '@deessejs/fp';

// Using tap for logging without breaking the chain
const result = pipe(
  search(query),
  tap(r => isErr(r) ? console.error(`Error: ${r.error.message}`) : null),
  mapErr(e => e.addNotes(`Search attempted at ${new Date().toISOString()}`))
);
```

## Implementation Notes

Following the [deesse-fp try rules](../../../.claude/skills/deesse-fp/rules/try.md), we wrap throwing functions with `attempt` / `fromPromise`.

Using [pipe & flow patterns](../../../.claude/skills/deesse-fp/rules/pipe-flow.md) for cleaner composition.

### Search Implementation

```typescript
import { pipe, ok, fromPromise, map, mapErr } from '@deessejs/fp';
import { Exa } from 'exa-js';
import { SearchError } from './errors';

export function createSearch(exa: Exa) {
  return (options: SearchOptions): AsyncResult<SearchResponse, ReturnType<typeof SearchError>> =>
    pipe(
      exa.search(options.query, {
        numResults: options.numResults ?? 10,
        type: options.type ?? 'auto',
        highlights: options.highlights,
        text: options.text,
        contents: options.contents,
      }),
      fromPromise,
      map(response => ({
        results: response.results,
        requestId: response.requestId,
        autopromptString: response.autopromptString,
        costDollars: response.costDollars,
        statuses: response.statuses,
      })),
      mapErr(e =>
        SearchError({ query: options.query, reason: e.message })
          .addNotes('Exa search operation failed')
      )
    );
}
```

### Fetch Implementation

```typescript
import { pipe, ok, fromPromise, map, mapErr } from '@deessejs/fp';
import { Exa } from 'exa-js';
import { FetchError } from './errors';

export function createFetch(exa: Exa) {
  return (
    urls: string | string[] | SearchResult[],
    options?: FetchOptions
  ): AsyncResult<FetchResponse, ReturnType<typeof FetchError>> =>
    pipe(
      exa.getContents(urls, {
        text: options?.text,
        highlights: options?.highlights,
      }),
      fromPromise,
      map(response => ({
        results: response.results,
        requestId: response.requestId,
        costDollars: response.costDollars,
        statuses: response.statuses,
      })),
      mapErr(e =>
        FetchError({ url: Array.isArray(urls) ? urls[0] : urls, reason: e.message })
          .addNotes('Exa getContents operation failed')
      )
    );
}
```

## createFresh Factory

The `createFresh` function composes `createSearch` and `createFetch` into a single instance:

```typescript
import { Exa } from 'exa-js';
import { createSearch } from './search';
import { createFetch } from './fetch';

export interface FreshOptions {
  apiKey?: string;
}

export interface FreshInstance {
  search: ReturnType<typeof createSearch>;
  fetch: ReturnType<typeof createFetch>;
}

export function createFresh(options: FreshOptions = {}): FreshInstance {
  const exa = new Exa(options.apiKey);
  return {
    search: createSearch(exa),
    fetch: createFetch(exa),
  };
}
```

## Integration Points

### With apps/web

```typescript
// apps/web/src/lib/exa.ts
import { createFresh } from '@fresh/core';

export const fresh = createFresh({
  apiKey: process.env.EXA_API_KEY,
});

// Usage in a server action or API route
const result = await fresh.search({ query: 'AI news', numResults: 5 });
if (isErr(result)) {
  return { error: result.error.message };
}
return { data: result.value };
```

### With apps/cli (future)

```typescript
// apps/cli/src/commands/search.ts
import { createFresh } from '@fresh/core';
import { isOk } from '@deessejs/fp';

export const fresh = createFresh();

export async function handleSearch(query: string, options: SearchOptions) {
  const result = await fresh.search({ query, ...options });

  if (isErr(result)) {
    console.error(`Error: ${result.error.message}`);
    return;
  }

  console.log(JSON.stringify(result.value, null, 2));
}
```

## Alternatives Considered

### 1. Direct API Calls (without SDK)

- More control over request/response
- More error-prone
- No type safety
- **Rejected**: SDK provides better DX

### 2. Use searchAndContents instead of separate calls

- Combines search + fetch in one API call
- More efficient for combined use cases
- Less flexible for separate search/fetch UI
- **Decision**: Support both separate calls AND combined

### 3. Full Fresh SDK with API key management

- Adds complexity (API key, rate limiting, retries)
- Not needed for MVP
- **Deferred**: Add when SDK is published publicly

## Next Steps

1. Create `packages/core` directory structure
2. Implement `fresh.ts` with `createFresh()` factory
3. Implement `search.ts` and `fetch.ts`
4. Add types and error factory functions
5. Test integration with `apps/web`
6. Document usage in README

## References

- [Exa.ai TypeScript SDK](https://exa.ai/docs/sdks/typescript-sdk-specification)
- [Exa.js npm package](https://www.npmjs.com/package/exa-js)
- [Fresh Features Specs](../../features/)
- [Fresh SDK Spec](../../internal/packages/sdk/)
- [deesse-fp error rules](../../../.claude/skills/deesse-fp/rules/error.md)
- [deesse-fp error handling rules](../../../.claude/skills/deesse-fp/rules/error-handling.md)
- [deesse-fp try rules](../../../.claude/skills/deesse-fp/rules/try.md)
- [deesse-fp pipe-flow rules](../../../.claude/skills/deesse-fp/rules/pipe-flow.md)
