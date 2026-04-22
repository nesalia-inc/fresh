# Fresh SDK

TypeScript/JavaScript SDK for integrating Fresh into your applications.

## Overview

The Fresh SDK provides a programmatic interface to all Fresh features: `search`, `fetch`, `ask`, and `research`. It handles API authentication, request management, streaming responses, and job lifecycle.

## Installation

```bash
npm install @fresh/sdk
# or
yarn add @fresh/sdk
# or
pnpm add @fresh/sdk
```

## Quick Start

```typescript
import { createClient } from '@fresh/sdk';

const client = createClient({
  apiKey: process.env.FRESH_API_KEY
});

// Search the web
const searchResults = await client.search('latest AI developments', {
  numResults: 10
});

// Fetch content from URLs
const pages = await client.getContents([
  'https://example.com/article1',
  'https://example.com/article2'
], {
  text: { maxCharacters: 2000 }
});

// Ask a question
const answer = await client.ask('What is the latest version of React?', {
  wait: true
});

// Deep research
const report = await client.research('Impact of AI on healthcare', {
  depth: 3,
  branches: 5,
  wait: true
});
```

## Configuration

### createClient Options

```typescript
const client = createClient({
  apiKey: string;           // Required: Your Fresh API key
  baseUrl?: string;         // Default: 'https://api.fresh.dev'
  timeout?: number;         // Default: 60000 (ms)
  maxRetries?: number;      // Default: 3
  headers?: Record<string, string>;  // Custom headers
});
```

### Environment Variable

Set your API key via environment variable to avoid hardcoding:

```bash
export FRESH_API_KEY=your-api-key
```

```typescript
const client = createClient({
  apiKey: process.env.FRESH_API_KEY
});
```

## Authentication

Fresh uses API Key authentication. Keys can be created, managed, and revoked via the API or CLI.

### API Key Management

#### Create API Key

```typescript
// Via REST API
POST /api-key/create
{
  "name": "My API Key",
  "expiresIn": 60 * 60 * 24 * 30,  // 30 days
  "metadata": { "purpose": "development" }
}
```

#### List API Keys

```typescript
// Via REST API
GET /api-key/list?limit=10&offset=0

// Response
{
  "keys": [
    {
      "id": "key_abc123",
      "name": "My API Key",
      "prefix": "fresh_sk_***",
      "expiresAt": "2025-04-15T00:00:00Z",
      "createdAt": "2025-03-15T00:00:00Z",
      "lastUsedAt": "2025-03-20T00:00:00Z",
      "metadata": { "purpose": "development" }
    }
  ],
  "total": 5
}
```

#### Revoke API Key

```typescript
// Via REST API
POST /api-key/delete
{
  "id": "key_abc123"
}
```

### API Key Features

| Feature | Description |
|---------|-------------|
| **Prefix** | Keys start with `fresh_sk_` for identification |
| **Expiration** | Set custom expiration (default: 30 days) |
| **Metadata** | Attach custom metadata to keys |
| **Rate limiting** | Built-in rate limits per key |
| **Usage tracking** | `lastUsedAt` timestamp |

### CLI Management

Alternatively, manage API keys via the CLI:

```bash
# List API keys
fresh api-key list

# Create new API key
fresh api-key create --name "My Key" --expires-in 30d

# Revoke API key
fresh api-key revoke <key-id>
```

### Using API Keys

Pass your API key when creating the client:

```typescript
import { createClient } from '@fresh/sdk';

const client = createClient({
  apiKey: 'fresh_sk_your-api-key-here'
});
```

### Verify API Key (Server-side)

```typescript
// Verify a key from request headers
const verified = await auth.api.verifyApiKey({
  body: {
    key: request.headers.get('x-api-key')
  }
});

if (verified.user) {
  // Key belongs to user
  console.log(`Authorized for user: ${verified.user.id}`);
}
```

## Search

Web search powered by Exa.ai with multiple search types.

### Method Signature

```typescript
search(
  query: string,
  options?: SearchOptions
): Promise<SearchResult>
```

### SearchOptions

```typescript
interface SearchOptions {
  type?: 'auto' | 'fast' | 'deep-lite' | 'deep' | 'deep-reasoning' | 'instant';
  numResults?: number;              // Default: 10
  highlights?: {
    query?: string;
    maxCharacters?: number;         // Default: 200
  };
  text?: {
    maxCharacters?: number;        // Default: 1000
  };
  contents?: ContentOptions;
}
```

### Example

```typescript
// Basic search
const result = await client.search('hottest AI startups 2024');

// Deep search with highlights
const deep = await client.search('AI regulations impact', {
  type: 'deep',
  numResults: 20,
  highlights: { query: 'policy compliance', maxCharacters: 300 },
  text: { maxCharacters: 2000 }
});

// Deep reasoning with synthesis
const reasoning = await client.search('best strategy for AI adoption', {
  type: 'deep-reasoning',
  numResults: 10
});

if (reasoning.output) {
  console.log(reasoning.output.content);
  reasoning.output.grounding.forEach(g => {
    g.citations.forEach(c => console.log(`  - ${c.title}: ${c.url}`));
  });
}
```

### Response

```typescript
interface SearchResult {
  autopromptString: string;
  results: Array<{
    title: string;
    id: string;
    url: string;
    publishedDate?: string;
    author?: string;
    text?: string;
  }>;
  requestId: string;
  costDollars: {
    stDollars: number;
    totalCost: number;
  };
  statuses: Array<{
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

## Fetch

Retrieve content from URLs using Exa.getContents.

### Method Signature

```typescript
getContents(
  urls: string | string[] | SearchResult[],
  options?: FetchOptions
): Promise<FetchResult>
```

### FetchOptions

```typescript
interface FetchOptions {
  text?: {
    maxCharacters?: number;        // Default: 1000
  };
  highlights?: {
    query?: string;
    maxCharacters?: number;       // Default: 200
  };
}
```

### Example

```typescript
// Single URL
const result = await client.getContents('https://example.com/article');

// Multiple URLs
const results = await client.getContents([
  'https://example.com/article1',
  'https://example.com/article2',
  'https://example.com/article3'
], {
  text: { maxCharacters: 3000 },
  highlights: { query: 'AI', maxCharacters: 150 }
});

results.results.forEach(doc => {
  console.log(`Title: ${doc.title}`);
  console.log(`Content: ${doc.text}`);
  console.log(`URL: ${doc.url}`);
});
```

### Response

```typescript
interface FetchResult {
  results: Array<{
    url: string;
    id: string;
    title?: string;
    text?: string;
  }>;
  requestId: string;
  costDollars: {
    stDollars: number;
    totalCost: number;
  };
  statuses: Array<{
    code: 'success' | 'error' | 'notFound' | 'unavailable';
    url: string;
  }>;
}
```

## Ask

Ask questions with AI-powered web research.

### Method Signature

```typescript
ask(
  query: string,
  options?: AskOptions
): Promise<AskJob>
```

### AskOptions

```typescript
interface AskOptions {
  format?: 'markdown' | 'json' | 'text';   // Default: 'markdown'
  maxSources?: number;                      // Default: 10
  model?: string;                           // Default: 'auto'
  wait?: boolean;                           // Default: false
  stream?: boolean;                         // Default: false
}
```

### Non-blocking Ask

```typescript
// Start job and get immediately
const job = await client.ask('What is the last version of React?');
console.log(job.jobId); // "ask_abc123"

// Poll for completion
while (job.status === 'running') {
  await new Promise(r => setTimeout(r, 1000));
  await job.refresh();
}

if (job.status === 'completed') {
  console.log(job.answer);
}
```

### Wait for Completion

```typescript
const result = await client.ask('Latest AI news', { wait: true });
console.log(result.answer);
```

### Streaming

```typescript
const stream = await client.ask('Latest AI news', { stream: true });

for await (const event of stream) {
  switch (event.type) {
    case 'status':
      console.log(`Progress: ${event.data.phase} (${event.data.progress}/${event.data.total})`);
      break;
    case 'answer':
      process.stdout.write(event.data.content);
      break;
    case 'done':
      console.log(`\nTotal cost: $${event.data.totalCost}`);
      break;
  }
}
```

### AskJob Object

```typescript
interface AskJob {
  jobId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  createdAt: string;
  answer?: string;
  sources?: Array<{
    url: string;
    title: string;
    relevance: number;
    citedAt: string;
  }>;
  meta?: {
    model: string;
    researchTimeMs: number;
    totalCost: number;
  };

  // Methods
  refresh(): Promise<AskJob>;
  cancel(): Promise<void>;
}
```

## Research

Deep multi-branch research with tree-of-thought reasoning.

### Method Signature

```typescript
research(
  query: string,
  options?: ResearchOptions
): Promise<ResearchJob>
```

### ResearchOptions

```typescript
interface ResearchOptions {
  depth?: number;                 // Default: 3
  branches?: number;               // Default: 4
  format?: 'markdown' | 'json' | 'text';  // Default: 'markdown'
  model?: string;                  // Default: 'auto'
  cite?: boolean;                  // Default: true
  wait?: boolean;                  // Default: false
  stream?: boolean;                // Default: false
}
```

### Example

```typescript
// Start research job
const job = await client.research('Impact of AI on software development', {
  depth: 3,
  branches: 5
});

// Wait for completion
const result = await client.research('Impact of AI on software development', {
  depth: 4,
  branches: 6,
  wait: true
});

console.log(result.report);
console.log(`Cost: $${result.stats.totalCost}`);
console.log(`Sources: ${result.stats.totalSources}`);
console.log(`Branches: ${result.stats.branchesExplored}`);
```

### Streaming Research

```typescript
const stream = await client.research('AI regulations', {
  depth: 3,
  stream: true
});

for await (const event of stream) {
  switch (event.type) {
    case 'status':
      console.log(`Branch ${event.data.current}/${event.data.total} (depth ${event.data.depth})`);
      break;
    case 'finding':
      console.log(`Finding: ${event.data.finding.substring(0, 100)}...`);
      break;
    case 'branch_complete':
      console.log(`Completed branch: ${event.data.branch} (${event.data.sources} sources)`);
      break;
    case 'report':
      process.stdout.write(event.data.content);
      break;
    case 'done':
      console.log(`\nResearch complete!`);
      console.log(`Total cost: $${event.data.totalCost}`);
      console.log(`Total sources: ${event.data.totalSources}`);
      break;
  }
}
```

### ResearchJob Object

```typescript
interface ResearchJob {
  jobId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  createdAt: string;
  report?: string;
  tree?: ResearchTree;
  stats?: {
    totalSources: number;
    branchesExplored: number;
    totalDepth: number;
    researchTimeMs: number;
    totalCost: number;
  };
  meta?: {
    model: string;
    requestId: string;
  };

  // Methods
  refresh(): Promise<ResearchJob>;
  cancel(): Promise<void>;
}
```

### ResearchTree Structure

```typescript
interface ResearchTree {
  query: string;
  branches: Array<{
    id: string;
    title: string;
    status: 'pending' | 'exploring' | 'completed' | 'failed';
    sources: Array<{
      url: string;
      title: string;
      relevance: number;
    }>;
    findings: string[];
    subBranches: ResearchTreeNode[];
  }>;
}
```

## Job Management

All async operations (ask, research) return job objects with management methods.

### Refresh

```typescript
const job = await client.ask('What is React 19?');
// ... time passes ...
await job.refresh();
console.log(job.status);
```

### Cancel

```typescript
const job = await client.research('Complex topic', { wait: true });

if (/* something */) {
  await job.cancel();
}
```

## Error Handling

```typescript
import { FreshError, RateLimitError, AuthError } from '@fresh/sdk';

try {
  const result = await client.search('query');
} catch (error) {
  if (error instanceof AuthError) {
    console.error('Invalid API key');
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded');
    console.error(`Retry after: ${error.retryAfter}s`);
  } else if (error instanceof FreshError) {
    console.error(`Fresh error: ${error.code}`);
    console.error(error.message);
  }
}
```

### Error Types

| Class | Code | Description |
|-------|------|-------------|
| `FreshError` | Base error | Generic Fresh error |
| `AuthError` | `UNAUTHORIZED` | Invalid API key |
| `RateLimitError` | `RATE_LIMITED` | Rate limit exceeded |
| `NotFoundError` | `NOT_FOUND` | Resource not found |
| `ValidationError` | `INVALID_INPUT` | Invalid parameters |

## TypeScript

The SDK is written in TypeScript and exports all types:

```typescript
import type {
  SearchOptions,
  SearchResult,
  FetchOptions,
  FetchResult,
  AskOptions,
  AskJob,
  ResearchOptions,
  ResearchJob,
  ResearchTree,
  FreshError,
  RateLimitError
} from '@fresh/sdk';
```

## Browser Usage

The SDK works in browser environments with CORS support:

```typescript
import { createClient } from '@fresh/sdk';

const client = createClient({
  apiKey: 'your-api-key' // Be careful with API keys in browsers
});
```

For browser usage, consider using environment variables or a backend proxy to protect your API key.

## Related

- [CLI](../apps/cli/README) - Command-line interface
- [fetch](../features/fetch/README) - Content extraction
- [search](../features/search/README) - Web search
- [ask](../features/ask/README) - Question answering
- [research](../features/research/README) - Deep research
