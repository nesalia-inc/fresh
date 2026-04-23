# API Key Plugin

## Overview

The API Key plugin for Better Auth enables authentication via static API keys with built-in rate limiting, expiration, and quota management.

## Installation

```bash
npm install @better-auth/api-key
```

### Server Setup

```typescript
// auth.ts
import { betterAuth } from "better-auth"
import { apiKey } from "@better-auth/api-key"

export const auth = betterAuth({
  plugins: [
    apiKey()
  ]
})
```

### Client Setup

```typescript
// auth-client.ts
import { createAuthClient } from "better-auth/client"
import { apiKeyClient } from "@better-auth/api-key/client"

export const authClient = createAuthClient({
  plugins: [apiKeyClient()]
})
```

### Database Migration

```bash
npx auth migrate
# or
npx auth generate
```

---

## Features

| Feature | Description |
|---------|-------------|
| Create/manage/verify API keys | Full lifecycle management |
| Built-in rate limiting | Per-key request limits |
| Custom expiration | `expiresIn` parameter |
| Remaining count | Request quota with refill |
| Metadata | Custom data attached to keys |
| Custom prefix | Key prefix for identification |
| Sessions from API keys | Auto-create sessions |
| Multiple configurations | Different key types |
| Organization-owned keys | Team API keys |

---

## Basic Usage

### Create an API Key

```typescript
// Client
const { data, error } = await authClient.apiKey.create({
  configId,           // Optional: configuration ID
  name: "project-api-key",
  expiresIn: 60 * 60 * 24 * 7,  // 7 days in seconds
  prefix: "project",
  metadata: { plan: "pro" }
});

// Server (without session headers)
const data = await auth.api.createApiKey({
  body: {
    configId,
    name: "project-api-key",
    expiresIn: 60 * 60 * 24 * 7,
    userId: "user-id",  // Required server-side
    prefix: "project",
    metadata: { plan: "pro" }
  }
});
```

**Returns:** `ApiKey` object including the `key` value (only shown once!)

### Verify an API Key

```typescript
// Client
const { data, error } = await authClient.apiKey.verify({
  configId,
  key: "your_api_key_here",
  permissions: {         // Optional permissions check
    projects: ["read", "read-write"]
  }
});

// Server
const data = await auth.api.verifyApiKey({
  body: {
    configId,
    key: "your_api_key_here",
    permissions: { projects: ["read"] }
  }
});
```

**Result:**
```typescript
{
  valid: boolean;
  error: { message: string; code: string } | null;
  key: Omit<ApiKey, "key"> | null;  // Everything except the key itself
}
```

### Get API Key Details

```typescript
// Get without key value
const { data } = await authClient.apiKey.get({
  configId,
  id: "some-api-key-id"
});
```

### Update an API Key

```typescript
// Enable/Disable, update remaining, refill
const { data } = await authClient.apiKey.update({
  configId,
  keyId: "some-api-key-id",
  name: "new-name"
});

// Server-only properties
await auth.api.updateApiKey({
  body: {
    keyId: "some-api-key-id",
    enabled: true,
    remaining: 100,
    refillAmount: 100,
    refillInterval: 1000,  // ms
    rateLimitEnabled: true,
    rateLimitTimeWindow: 1000,
    rateLimitMax: 100
  }
});
```

### Delete an API Key

```typescript
const { data, error } = await authClient.apiKey.delete({
  configId,
  keyId: "some-api-key-id"
});
```

### List API Keys

```typescript
// User-owned keys
const result = await authClient.apiKey.list({
  query: {
    configId,
    limit: 20,
    offset: 0,
    sortBy: "createdAt",
    sortDirection: "desc"
  }
});

// Organization-owned keys
const orgKeys = await authClient.apiKey.list({
  query: { organizationId: "org_123" }
});
```

**Result:**
```typescript
{
  apiKeys: Omit<ApiKey, "key">[];
  total: number;
  limit?: number;
  offset?: number;
}
```

---

## Advanced Features

### Rate Limiting

```typescript
// Create with rate limiting
const { data } = await auth.api.createApiKey({
  body: {
    name: "rate-limited-key",
    rateLimitEnabled: true,
    rateLimitTimeWindow: 1000,    // 1 second window
    rateLimitMax: 10              // 10 requests per window
  }
});
```

### Remaining Count & Refill

```typescript
// Create with quota
const { data } = await auth.api.createApiKey({
  body: {
    name: "quota-key",
    remaining: 100,           // 100 requests
    refillAmount: 100,        // Refill amount
    refillInterval: 1000     // Refill every second (ms)
  }
});

// Update remaining
await auth.api.updateApiKey({
  body: {
    keyId: "key-id",
    remaining: 50
  }
});
```

### Permissions

```typescript
// Create with permissions
const { data } = await auth.api.createApiKey({
  body: {
    name: "project-key",
    permissions: {
      projects: ["read", "write"],
      billing: ["read"]
    }
  }
});

// Verify with permissions check
const { data } = await auth.api.verifyApiKey({
  body: {
    key: "xxx-yyy-zzz",
    permissions: {
      projects: ["read"]  // Must have at least "read"
    }
  }
});
```

### Multiple Configurations

```typescript
// auth.ts - multiple API key types
export const auth = betterAuth({
  plugins: [
    apiKey({
      configs: {
        "public": {   // Public API key config
          expiresIn: 60 * 60 * 24 * 365,  // 1 year
        },
        "internal": { // Internal API key config
          expiresIn: 60 * 60 * 24 * 30,   // 30 days
          rateLimitEnabled: true,
          rateLimitMax: 1000,
        }
      }
    })
  ]
});

// Use specific config
const { data } = await authClient.apiKey.create({
  configId: "internal",
  name: "internal-key"
});
```

### Organization-Owned Keys

```typescript
// Create for organization
const { data } = await authClient.apiKey.create({
  organizationId: "org-id",  // Required for org keys
  name: "org-api-key"
});

// Verify org key
const { data } = await auth.api.verifyApiKey({
  body: {
    key: "org-key",
    permissions: { "org-repos": ["read"] }
  }
});
```

### Metadata

```typescript
// Attach custom data
const { data } = await auth.api.createApiKey({
  body: {
    name: "my-key",
    metadata: {
      plan: "pro",
      tier: "enterprise",
      maxRequests: 10000
    }
  }
});

// Update metadata
await auth.api.updateApiKey({
  body: {
    keyId: "key-id",
    metadata: { plan: "enterprise", approved: true }
  }
});
```

---

## Use Cases for fresh-final

### CLI Authentication

The current CLI uses device authorization. API keys could replace or supplement this:

```typescript
// CLI could use API key instead of device code
const apiKey = await authClient.apiKey.create({
  name: "CLI - " + hostname,
  expiresIn: 60 * 60 * 24 * 365,  // 1 year
  metadata: { device: hostname }
});

// CLI sends API key in header
Authorization: Bearer xxx-yyy-zzz
```

### Rate-Limited API Access

```typescript
// Create API key with usage limits
const { data } = await auth.api.createApiKey({
  body: {
    name: "pro-user-key",
    remaining: 1000,           // 1000 requests
    refillAmount: 1000,
    refillInterval: 60 * 60 * 24 * 30,  // Monthly refill (ms)
    rateLimitEnabled: true,
    rateLimitTimeWindow: 1000,
    rateLimitMax: 100
  }
});
```

### Programmatic Access

```typescript
// Server-side API key for internal services
const { data } = await auth.api.createApiKey({
  body: {
    name: "analytics-service",
    userId: "system-user",
    permissions: {
      search: ["read"],
      fetch: ["read"]
    }
  }
});

// Service uses key to access API
const result = await fetch("/api/search", {
  headers: { "Authorization": `Bearer ${data.key}` }
});
```

---

## Schema

The API key plugin adds the following to your schema:

```typescript
// api_key table
{
  id: string,           // Primary key
  name: string,         // Display name
  key: string,          // Hashed API key
  prefix: string,       // First few chars for identification
  userId: string,       // Owner (user or organization)
  organizationId: string | null,
  expiresAt: Date,
  enabled: boolean,
  remaining: number | null,
  refillAmount: number | null,
  refillInterval: number | null,
  lastRefillAt: Date | null,
  rateLimitEnabled: boolean,
  rateLimitTimeWindow: number | null,
  rateLimitMax: number | null,
  metadata: any | null,
  createdAt: Date,
  updatedAt: Date
}
```

---

## Resources

- [Official Documentation](https://better-auth.com/docs/plugins/api-key)
- [Advanced Features](https://better-auth.com/docs/plugins/api-key/advanced)
- [Reference](https://better-auth.com/docs/plugins/api-key/reference)
