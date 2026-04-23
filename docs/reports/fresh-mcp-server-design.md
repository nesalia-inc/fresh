# Fresh MCP Server Design Report

## Executive Summary

This report analyzes how to create an MCP (Model Context Protocol) server that exposes Fresh's search and fetch capabilities. The goal is to allow Claude Code (or any MCP-compatible client) to access Fresh's AI-powered web search and content extraction directly through natural language queries.

## Current Fresh Architecture

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `createFresh()` | `apps/web/src/core/fresh.ts` | Factory function creating Fresh instance with Exa.ai |
| Search | `apps/web/src/core/search.ts` | Wraps `exa.search()` with error handling |
| Fetch | `apps/web/src/core/fetch.ts` | Wraps `exa.getContents()` with error handling |
| API Routes | `apps/web/src/app/api/` | REST endpoints for search/fetch |
| Auth | `apps/web/src/deesse.config.ts` | Better Auth with device authorization + bearer tokens |

### Fresh Capabilities

**Search (`fresh.search`)**
- Query string (required)
- numResults (default 10)
- type: `auto` | `fast` | `deep-lite` | `deep` | `deep-reasoning` | `instant`
- includeDomains / excludeDomains
- startPublishedDate / endPublishedDate
- category: `company` | `research paper` | `news` | `pdf` | `personal site` | `financial report` | `people`
- highlights / text options

**Fetch (`fresh.fetch`)**
- urls: string | string[] (required)
- text options (maxCharacters, verbosity, etc.)
- highlights options

## MCP Server Design Options

### Option 1: Standalone MCP Server (Recommended)

Create a new package at `apps/mcp` that exposes Fresh as an MCP server.

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Claude Code   │ ──── │   Fresh MCP     │ ──── │    Exa.ai API   │
│   (MCP Host)    │ STDIO │   Server        │  HTTP │   (search/fetch)│
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                ▼
                         ┌─────────────────┐
                         │  Better Auth    │
                         │  API Key Plugin │
                         └─────────────────┘
```

**Project Structure:**
```
apps/mcp/
├── src/
│   └── index.ts        # MCP server entry point
├── package.json
└── tsconfig.json
```

**Pros:**
- Independent deployment
- Can be used by any MCP-compatible client
- Clear separation of concerns
- Follows project rules (functional-first)

**Cons:**
- Requires EXA_API_KEY management
- Need to handle Fresh auth separately
- Additional deployment artifact

### Option 2: Next.js API Route with MCP Protocol

Add MCP protocol support to the existing Next.js app by creating an MCP handler at `/api/mcp`.

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Claude Code   │ ──── │   Next.js App   │ ──── │    Exa.ai API   │
│   (MCP Host)    │ HTTP │   /api/mcp      │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                ▼
                         ┌─────────────────┐
                         │   Better Auth   │
                         │   (Session)     │
                         └─────────────────┘
```

**Pros:**
- Reuses existing auth infrastructure
- Single deployment
- No separate service to manage

**Cons:**
- MCP over HTTP is less common
- May have CORS/configuration issues
- Mixes concerns

### Option 3: Extend CLI with MCP Mode

Add an MCP server mode to the existing `fresh` CLI.

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Claude Code   │ ──── │   fresh mcp     │ ──── │    Exa.ai API   │
│   (MCP Host)    │ STDIO │   (CLI mode)    │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

**Pros:**
- Reuses CLI authentication (keytar)
- Single binary
- Consistent UX

**Cons:**
- Claude Code runs CLI differently than long-lived server
- Session management complexity
- More complex CLI

## Recommended Approach: Option 1 (Standalone MCP Server)

### Why Option 1

1. **Clean separation** - MCP server is a dedicated layer
2. **Reusable** - Works with Claude Code, Claude Desktop, or any MCP client
3. **Project rules compliant** - Functional-first, no classes
4. **Deployable** - Can be deployed separately if needed

### Implementation Plan

#### 1. Project Setup

```bash
mkdir apps/mcp
cd apps/mcp
npm init -y
npm install @modelcontextprotocol/sdk exa-js zod
npm install -D typescript @types/node
```

#### 2. Core Implementation

```typescript
// apps/mcp/src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { createFresh } from "@nesalia/fresh-core"; // or direct exa-js

const server = new McpServer({
  name: "fresh",
  version: "1.0.0",
});

// Initialize Fresh (reads EXA_API_KEY from env)
const fresh = createFresh({ apiKey: process.env.EXA_API_KEY });

// Register search tool
server.registerTool(
  "search",
  {
    description: "Search the web using AI-powered search",
    inputSchema: {
      query: z.string().describe("Search query text"),
      numResults: z.number().optional().describe("Maximum number of results (default: 10)"),
      type: z.enum(["auto", "fast", "deep-lite", "deep", "deep-reasoning", "instant"]).optional(),
      category: z.enum(["company", "research paper", "news", "pdf", "personal site", "financial report", "people"]).optional(),
      startPublishedDate: z.string().optional(),
      endPublishedDate: z.string().optional(),
      includeDomains: z.array(z.string()).optional(),
      excludeDomains: z.array(z.string()).optional(),
    },
  },
  async ({ query, numResults, type, category, startPublishedDate, endPublishedDate, includeDomains, excludeDomains }) => {
    const result = await fresh.search({
      query,
      numResults,
      type,
      category,
      startPublishedDate: startPublishedDate ? new Date(startPublishedDate) : undefined,
      endPublishedDate: endPublishedDate ? new Date(endPublishedDate) : undefined,
      includeDomains,
      excludeDomains,
    });

    if (!result.ok) {
      return {
        content: [{ type: "text", text: `Search failed: ${result.error.message}` }],
        isError: true,
      };
    }

    const value = result.value;
    const formatted = formatSearchResults(value);

    return {
      content: [{ type: "text", text: formatted }],
    };
  }
);

// Register fetch tool
server.registerTool(
  "fetch",
  {
    description: "Extract content from URLs",
    inputSchema: {
      urls: z.union([z.string(), z.array(z.string())]).describe("URL or list of URLs to fetch"),
      maxCharacters: z.number().optional().describe("Maximum characters to extract"),
      verbosity: z.enum(["compact", "standard", "full"]).optional(),
      highlightsPerUrl: z.number().optional(),
    },
  },
  async ({ urls, maxCharacters, verbosity, highlightsPerUrl }) => {
    const result = await fresh.fetch({
      urls,
      text: maxCharacters ? { maxCharacters } : undefined,
      verbosity,
      highlights: highlightsPerUrl ? { highlightsPerUrl } : undefined,
    });

    if (!result.ok) {
      return {
        content: [{ type: "text", text: `Fetch failed: ${result.error.message}` }],
        isError: true,
      };
    }

    const formatted = formatFetchResults(result.value);

    return {
      content: [{ type: "text", text: formatted }],
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Fresh MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
```

#### 3. Helper Functions

```typescript
function formatSearchResults(result: SearchResult): string {
  const lines = [`Found ${result.results.length} results:\n`];

  result.results.forEach((r, i) => {
    lines.push(`${i + 1}. ${r.title}`);
    lines.push(`   URL: ${r.url}`);
    if (r.score !== undefined) {
      lines.push(`   Score: ${(r.score * 100).toFixed(1)}%`);
    }
    if (r.highlights && r.highlights.length > 0) {
      const snippet = r.highlights[0].substring(0, 200);
      lines.push(`   ${snippet}${r.highlights[0].length > 200 ? "..." : ""}`);
    }
    lines.push("");
  });

  return lines.join("\n");
}

function formatFetchResults(result: FetchResult): string {
  const lines: string[] = [];

  result.results.forEach((r) => {
    lines.push(`URL: ${r.url}`);
    if (r.title) lines.push(`Title: ${r.title}`);
    if (r.author) lines.push(`Author: ${r.author}`);
    if (r.publishedDate) lines.push(`Published: ${r.publishedDate}`);
    lines.push("");
    if (r.text) {
      lines.push(r.text.substring(0, 2000));
    } else if (r.highlights && r.highlights.length > 0) {
      lines.push(r.highlights.join("\n\n"));
    }
    lines.push("\n" + "-".repeat(50) + "\n");
  });

  return lines.join("\n");
}
```

#### 4. Configuration

**package.json:**
```json
{
  "name": "@nesalia/fresh-mcp",
  "version": "0.1.0",
  "type": "module",
  "bin": {
    "fresh-mcp": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx watch src/index.ts"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "exa-js": "^2.11.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "tsx": "^4.19.0",
    "typescript": "^5.0.0"
  }
}
```

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

## Authentication Design

### Using Better Auth's API Key Plugin

Fresh already uses Better Auth. We can add the `@better-auth/api-key` plugin to enable API key authentication for the MCP server.

**Installation:**
```bash
npm install @better-auth/api-key
```

**Server Configuration** (`apps/web/src/deesse.config.ts`):
```typescript
import { apiKey } from "@better-auth/api-key"

export const config = defineConfig({
  // ... existing config
  plugins: [
    deviceAuthorization({...}),
    bearer(),
    apiKey()  // Add this
  ],
})
```

**Database Migration:**
```bash
npx auth migrate
# or
npx auth generate
```

This creates the `api_key` table needed for storing API keys.

### How It Works

| Method | Purpose |
|--------|---------|
| `authClient.apiKey.create()` | Create a new API key for the user |
| `authClient.apiKey.verify()` | Verify an API key's validity |
| `authClient.apiKey.list()` | List all user's API keys |
| `authClient.apiKey.delete()` | Revoke an API key |

### API Key Features

- **Custom expiration** - Set `expiresIn` (e.g., `60 * 60 * 24 * 7` for 1 week)
- **Rate limiting** - Built-in `rateLimitMax` and `rateLimitTimeWindow`
- **Metadata** - Attach custom data like key purpose
- **Custom prefixes** - Start keys with custom prefixes (e.g., `fresh_`)
- **Refill system** - Automatic key refills for quota management

### Creating an API Key (Frontend)

```typescript
// In the Fresh web app - Settings page
const { data, error } = await authClient.apiKey.create({
  name: "Claude Code",
  expiresIn: 60 * 60 * 24 * 365, // 1 year
  metadata: {
    service: "claude-code",
    createdAt: new Date().toISOString(),
  },
});

// data.key contains the full API key (only shown once!)
// User must copy it immediately
```

### Verifying an API Key (MCP Server)

```typescript
// In the MCP server or API route
const { valid, key, error } = await auth.apiKey.verify({
  key: "fresh_abc123...", // API key from header
});

// If valid, key.userId contains the user ID
// Use key.userId to associate the request with a user
```

### MCP Server Usage

The MCP server would verify the API key on each request:

```typescript
// apps/mcp/src/index.ts
import { betterAuth } from "better-auth"
import { apiKey } from "@better-auth/api-key"

const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
  plugins: [apiKey()],
})

// In tool handler:
async function searchTool({ apiKey }: { apiKey: string }) {
  const { valid, key } = await auth.apiKey.verify({ key: apiKey })

  if (!valid) {
    return { content: [{ type: "text", text: "Invalid API key" }], isError: true }
  }

  // Use key.userId to track usage, apply rate limits, etc.
  const result = await fresh.search({...})
  return { content: [{ type: "text", text: formatResults(result) }] }
}
```

### User Flow for MCP Setup

1. User logs into Fresh web app
2. Goes to Settings > API Keys
3. Clicks "Create API Key"
4. Names it "Claude Code" and sets expiration
5. Copies the key (shown only once)
6. Configures Claude Code:
   ```bash
   claude mcp add fresh --transport http https://api.nesalia.com/mcp \
     --header "x-api-key: $FRESH_API_KEY"
   ```

### Alternative: MCP Server with Stdio

If the MCP server runs as a separate process:

```bash
claude mcp add fresh --transport stdio -- \
  npx -y @nesalia/fresh-mcp --api-key "$FRESH_API_KEY"
```

The MCP server receives the API key as an environment variable or startup argument.

## MCP Tool Definitions

### Tool: `search`

```json
{
  "name": "search",
  "description": "Search the web using AI-powered search (similar to Google but smarter). Use this when you need to find current information, research topics, or discover web resources.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query. Be specific and use natural language."
      },
      "numResults": {
        "type": "number",
        "description": "Number of results to return (default: 10, max: 100)"
      },
      "type": {
        "type": "string",
        "enum": ["auto", "fast", "deep-lite", "deep", "deep-reasoning", "instant"],
        "description": "Search type: auto (balanced), fast (quick), deep-lite (moderate depth), deep (thorough), deep-reasoning (AI reasoning), instant (fastest)"
      },
      "category": {
        "type": "string",
        "enum": ["company", "research paper", "news", "pdf", "personal site", "financial report", "people"],
        "description": "Filter by content type"
      },
      "startPublishedDate": {
        "type": "string",
        "description": "Start date filter (ISO 8601 format, e.g., 2024-01-01)"
      },
      "endPublishedDate": {
        "type": "string",
        "description": "End date filter (ISO 8601 format)"
      },
      "includeDomains": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Only include results from these domains"
      },
      "excludeDomains": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Exclude results from these domains"
      }
    },
    "required": ["query"]
  }
}
```

### Tool: `fetch`

```json
{
  "name": "fetch",
  "description": "Extract and summarize content from URLs. Use this when you need to read the full content of a webpage, article, or document.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "urls": {
        "oneOf": [
          { "type": "string" },
          { "type": "array", "items": { "type": "string" } }
        ],
        "description": "URL or list of URLs to fetch"
      },
      "maxCharacters": {
        "type": "number",
        "description": "Maximum characters to extract per URL (default: 5000)"
      },
      "verbosity": {
        "type": "string",
        "enum": ["compact", "standard", "full"],
        "description": "How detailed the extraction should be"
      },
      "highlightsPerUrl": {
        "type": "number",
        "description": "Number of key highlights to extract"
      }
    },
    "required": ["urls"]
  }
}
```

## Claude Code Integration

### User Setup Flow

1. User installs Fresh MCP: `claude mcp add fresh --transport http https://mcp.nesalia.com --header "Authorization: Bearer $FRESH_API_KEY"`
2. User gets API key from Fresh web app (Settings > API Keys)
3. User configures Claude Code with their API key
4. Claude Code can now use Fresh tools

### Example Conversations

**User:** "Search for the latest news about AI agents"
**Claude uses `search` tool:** `search({ query: "AI agents latest news", type: "news", numResults: 5 })`

**User:** "Summarize the content of these URLs"
**Claude uses `fetch` tool:** `fetch({ urls: ["https://example.com/article1", "https://example.com/article2"] })`

**User:** "Find posts about Next.js 16 from the past month"
**Claude uses `search` tool:** `search({ query: "Next.js 16", startPublishedDate: "2025-03-01", category: "news" })`

## Security Considerations

1. **API Key Storage** - Users should store their Fresh API key securely
2. **Rate Limiting** - Implement per-user rate limits in MCP server
3. **Input Validation** - Zod schemas validate all tool inputs
4. **Output Sanitization** - Handle potentially malicious HTML/content
5. **CORS** - If using HTTP transport, configure appropriately

## Deployment Options

### Option 1: Separate Service
```
https://mcp.nesalia.com  (Node.js server with stdio or HTTP)
```

### Option 2: Part of Existing API
```
https://api.nesalia.com/mcp  (New endpoint on existing Next.js app)
```

### Option 3: Edge Function
```
Vercel Edge Function handling MCP protocol
```

## Next Steps

1. **Install `@better-auth/api-key`** package
2. **Run database migration** - `npx auth migrate` to create api_key table
3. **Update deesse.config.ts** - Add `apiKey()` to plugins array
4. **Create API key management UI** - Add page in Fresh web app for users to create/revoke keys
5. **Create MCP package** in `apps/mcp/` with search and fetch tools
6. **Implement API key verification** in MCP server
7. **Deploy MCP server** (separate service or `/api/mcp` endpoint)
8. **Test with Claude Code** - `claude mcp add fresh ...`
9. **Write user documentation** for MCP setup

## Appendix: MCP SDK Reference

### Key Packages

- `@modelcontextprotocol/sdk` - Official MCP SDK for TypeScript
- `zod` - Schema validation (already in project)

### Important Notes

1. **Stdio transport** - For CLI-based MCP servers, use `StdioServerTransport`
2. **Logging** - Use `console.error()` for logs (stdout is reserved for JSON-RPC)
3. **Error handling** - Return errors in tool response with `isError: true`
4. **Tool naming** - Use snake_case: `search`, `fetch`, `get_weather`

### Resources

- [MCP Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [MCP SDK Reference](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [MCP Registry](https://github.com/modelcontextprotocol/servers)
