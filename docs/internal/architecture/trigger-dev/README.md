# Trigger.dev Integration

Background job processing for Fresh using Trigger.dev.

## Overview

Fresh uses Trigger.dev for reliable background job processing. It handles long-running AI tasks, research jobs, and complex workflows with built-in queuing, automatic retries, and real-time monitoring.

## Why Trigger.dev?

| Feature | Benefit |
|---------|---------|
| **No timeouts** | Long-running research tasks complete reliably |
| **Automatic retries** | Failed jobs retry with exponential backoff |
| **Real-time monitoring** | Track job progress via API or React hooks |
| **Built-in queuing** | Handle burst traffic without overwhelming resources |
| **Open source** | Self-host if needed |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Fresh API                             │
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │  Ask    │───▶│ Trigger │───▶│  Job    │                  │
│  │ Request │    │   CLI   │    │  Queue  │                  │
│  └─────────┘    └─────────┘    └────┬────┘                  │
│                                     │                        │
│                    ┌────────────────┼────────────────┐       │
│                    ▼                ▼                ▼       │
│              ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│              │ Research │    │  Fetch   │    │  Search  │    │
│              │  Worker  │    │  Worker  │    │  Worker  │    │
│              └──────────┘    └──────────┘    └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Install Trigger.dev SDK

```bash
npm install @trigger.dev/sdk
```

### 2. Install CLI

```bash
npm install -g @trigger.dev/cli
```

### 3. Login

```bash
trigger.dev login
```

### 4. Initialize in project

```bash
npx trigger.dev init
```

## Configuration

### Environment Variables

```bash
TRIGGER_API_KEY=tr_dev_xxxxxxxxxxxxx
TRIGGER_PUBLIC_API_KEY=tr_pk_xxxxxxxxxxxxx
```

### Create a client

```typescript
// lib/trigger.ts
import { TriggerClient } from "@trigger.dev/sdk";

export const client = new TriggerClient({
  id: "fresh-backend",
  apiKey: process.env.TRIGGER_API_KEY,
});
```

## Jobs

### Research Job

```typescript
// jobs/research.ts
import { client } from "@/lib/trigger";
import { Trigger } from "@trigger.dev/sdk";
import { exa } from "@/lib/exa";

const trigger = new Trigger({
  client,
  id: "deep-research",
});

trigger.on("research.start", async (task) => {
  const { query, depth, branches } = task.payload;

  // Explore branch
  const searchResults = await exa.search(query, {
    numResults: 10,
  });

  // Fetch content for each result
  const contents = await exa.getContents(
    searchResults.results.map((r) => r.url)
  );

  // Synthesize results
  const report = await synthesizeResearch(query, contents);

  return { report, sources: searchResults.results };
});

client.define(trigger);
```

### Ask Job

```typescript
// jobs/ask.ts
import { client } from "@/lib/trigger";
import { Trigger } from "@trigger.dev/sdk";

const trigger = new Trigger({
  client,
  id: "ask-question",
});

trigger.on("ask.start", async (task) => {
  const { query, maxSources, format } = task.payload;

  // Multi-step research
  const sources = await researchQuestion(query, maxSources);

  // Generate answer
  const answer = await generateAnswer(query, sources, format);

  return { answer, sources };
});

client.define(trigger);
```

### Fetch Job (Batch)

```typescript
// jobs/fetch.ts
import { client } from "@/lib/trigger";
import { Trigger } from "@trigger.dev/sdk";

const trigger = new Trigger({
  client,
  id: "batch-fetch",
});

trigger.on("fetch.start", async (task) => {
  const { urls, options } = task.payload;

  // Process URLs in parallel with concurrency limit
  const results = await Promise.all(
    urls.map((url) => exa.getContents([url], options))
  );

  return { results };
});

client.define(trigger);
```

## Triggers

### Manual Trigger

```typescript
// Trigger a job manually
await client.sendEvent({
  name: "research.start",
  payload: {
    query: "Impact of AI on software development",
    depth: 3,
    branches: 5,
  },
});
```

### Scheduled Trigger

```typescript
const trigger = new Trigger({
  client,
  id: "daily-digest",
  schedule: {
    cron: "0 9 * * *", // Every day at 9 AM
  },
});

trigger.onSchedule(async () => {
  // Send daily research digest to subscribed users
  const users = await getSubscribedUsers();
  for (const user of users) {
    await sendDailyDigest(user);
  }
});
```

## Monitoring

### API for Job Status

```typescript
// Get job runs
const runs = await client.runs.list("deep-research", {
  limit: 10,
  status: "completed",
});

// Get specific run
const run = await client.runs.get("run_abc123");

console.log(run.status); // "completed"
console.log(run.output); // { report, sources }
```

### React Hooks

```typescript
import { useTask } from "@trigger.dev/react";

function ResearchStatus({ taskId }) {
  const { task, error, status } = useTask(taskId);

  if (status === "running") {
    return (
      <div>
        <p>Research in progress...</p>
        <p>Phase: {task.descriptor.currentPhase}</p>
      </div>
    );
  }

  if (status === "completed") {
    return <div>Report: {task.output.report}</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }
}
```

### Real-time Webhooks

```typescript
// Subscribe to run events
client.on("run.completed", (event) => {
  console.log(`Run ${event.run.id} completed`);
  console.log(`Output: ${JSON.stringify(event.run.output)}`);
});

client.on("run.failed", (event) => {
  console.error(`Run ${event.run.id} failed: ${event.error.message}`);
});
```

## Concurrency & Queuing

```typescript
const trigger = new Trigger({
  client,
  id: "research-job",
  queue: {
    concurrencyKey: "research", // Limits concurrent runs per user
  },
});

trigger.on("research.start", async (task) => {
  // Only 3 research jobs run simultaneously per user
});
```

### Queue Options

| Option | Description | Default |
|--------|-------------|---------|
| `concurrencyKey` | Group runs by key | unlimited |
| `maxConcurrency` | Max concurrent runs | unlimited |
| `priority` | Priority (higher = first) | 0 |

## Retries

```typescript
const trigger = new Trigger({
  client,
  id: "research-job",
  retry: {
    maxAttempts: 3,
    exponentialBackoff: true,
    initialDelayMs: 1000,
  },
});
```

### Retry Strategy

| Attempt | Delay |
|---------|-------|
| 1 | 1 second |
| 2 | 2 seconds |
| 3 | 4 seconds |

## Error Handling

```typescript
trigger.on("research.start", async (task) => {
  try {
    const result = await performResearch(task.payload);
    return result;
  } catch (error) {
    if (error instanceof RateLimitError) {
      // Throw to trigger retry
      throw error;
    }
    if (error instanceof ValidationError) {
      // Don't retry, mark as failed
      return { error: error.message, failed: true };
    }
    throw error;
  }
});
```

## Fresh API Integration

### API Routes

```typescript
// app/api/ask/route.ts
import { client } from "@/lib/trigger";

export async function POST(request: Request) {
  const { query, options } = await request.json();

  // Send to Trigger.dev
  const run = await client.sendEvent({
    name: "ask.start",
    payload: { query, ...options },
  });

  return Response.json({
    jobId: run.id,
    status: "pending",
  });
}

// app/api/ask/[runId]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { runId: string } }
) {
  const run = await client.runs.get(params.runId);

  return Response.json({
    status: run.status,
    output: run.output,
  });
}
```

## Performance

### Benchmarks

| Operation | Duration |
|-----------|----------|
| Trigger send | ~50ms |
| Job start | ~200ms |
| Search (Exa) | ~500ms-2s |
| Fetch (10 URLs) | ~3-5s |
| Full research | ~10-60s |

### Limits

| Resource | Limit |
|----------|-------|
| Concurrent runs | 100 (configurable) |
| Max job runtime | No limit |
| Queue size | Unlimited |
| Retries | 10 max |

## Deployment

### Self-Hosting

Trigger.dev can be self-hosted:

```bash
docker run -d \
  --name trigger \
  -p 3030:3030 \
  -e DATABASE_URL=postgres://... \
  -e REDIS_URL=redis://... \
  triggerdotdev/trigger:latest
```

### Cloud

Use Trigger.dev Cloud for managed infrastructure:

```bash
# Deploy
npx trigger.dev deploy
```

## Related

- [Better Auth](../better-auth/README) - Authentication
- [SDK](../../packages/sdk/README) - TypeScript SDK
