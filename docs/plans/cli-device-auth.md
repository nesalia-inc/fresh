# Fresh CLI with Device Authorization Plan

## Overview

Create a CLI application (`apps/cli`) for Fresh that uses Better Auth's Device Authorization plugin (OAuth 2.0 RFC 8628) for secure, browser-based authentication. This allows users to log in to Fresh from terminals without typing passwords.

---

## Auth Architecture

### End-to-End Auth Flow

After CLI login, the `access_token` is a bearer token that must be validated by Fresh APIs for all subsequent requests.

```
┌──────────────────┐         ┌───────────────────┐         ┌─────────────────┐
│   Fresh CLI      │         │   Fresh Web API    │         │   Browser       │
│   (apps/cli)     │         │   (apps/web)      │         │   (user)        │
└────────┬─────────┘         └─────────┬─────────┘         └───────┬─────────┘
         │                             │                            │
         │  POST /device/code          │                            │
         │────────────────────────────▶│                            │
         │◀─ device_code, user_code,    │                            │
         │    verification_uri_complete │                            │
         │                             │                            │
         │  open(url)                 │                            │
         │────────────────────────────│── GET /device ────────────▶│
         │                             │                            │
         │                             │◀─ enter user code ─────────│
         │                             │                            │
         │                             │◀─ POST /device/approve ────│
         │                             │    (requires session)     │
         │                             │                            │
         │  POST /device/token         │                            │
         │  (poll every 5s, increase   │                            │
         │   by 5s on slow_down)       │                            │
         │────────────────────────────▶│                            │
         │                             │                            │
         │◀─ access_token, refresh_     │                            │
         │    token, expires_in        │                            │
         │                             │                            │
         │  STORE {                    │                            │
         │    access_token,           │                            │
         │    refresh_token,          │                            │
         │    expires_at,              │                            │
         │    scope,                   │                            │
         │    environment              │                            │
         │  }                          │                            │
         │                             │                            │
         │  GET /api/fresh.search     │                            │
         │  Authorization: Bearer <token>                           │
         │────────────────────────────▶│                            │
         │                             │─ validate bearer token ────▶│
         │◀─ search results            │                            │
```

### Post-Login Token Validation

All Fresh APIs that require authentication must:
1. Extract `Authorization: Bearer <token>` header
2. Validate token signature and expiry
3. Check token hasn't been revoked
4. Map token scopes to authorization rules

### Server Integration in `deesse.config.ts`

The device authorization plugin must be added to `apps/web/src/deesse.config.ts`, NOT `lib/deesse.ts`:

```typescript
// apps/web/src/deesse.config.ts
import { deviceAuthorization } from "better-auth/plugins"

const deesse = await createDeesse({
  database: drizzle({...}),
  plugins: [
    deviceAuthorization({
      // Client validation - only allow registered clients
      validateClient: (clientId) => {
        const allowedClients = ["fresh-cli", "fresh-web"]
        return allowedClients.includes(clientId)
      },
      verificationUri: "/device",
      expiresIn: "30m",
      interval: "5s",
      userCodeLength: 8,
      deviceCodeLength: 40,
      onDeviceAuthRequest: async (deviceRequest) => {
        // Audit log - NOT console.log in production
        logger.info({ event: "device_auth_request", ...deviceRequest })
      }
    }),
  ]
})
```

---

## RFC 8628 Compliance

### Polling Rules

1. **Initial interval**: 5 seconds (or server-specified `interval`)
2. **`authorization_pending`**: Continue polling with same interval
3. **`slow_down`**: Increase interval by 5 seconds (NOT double)
4. **`expired_token`**: Abort and prompt re-auth
5. **`access_denied`**: Abort and show denied message

```typescript
// Correct polling implementation
let currentInterval = interval

switch (data.error) {
  case "slow_down":
    currentInterval += 5000  // Increase by 5 seconds per RFC 8628
    await sleep(currentInterval)
    continue
  // ...
}
```

### Verification URI

Use `verification_uri_complete` when available (allows QR code or direct link):

```typescript
const { userCode, verificationUri, verificationUriComplete } = await requestDeviceCode()

if (verificationUriComplete) {
  console.log(`Open: ${verificationUriComplete}`)
} else {
  console.log(`Open: ${verificationUri} and enter: ${userCode}`)
}
```

Always continue displaying `userCode` even when `verification_uri_complete` is used.

---

## Device Verification Pages

### Page Structure

The verification flow spans three routes:

| Route | Auth | Purpose |
|-------|------|---------|
| `GET /device` | None | Show code entry form |
| `POST /device/approve` | Session | Approve pending device |
| `POST /device/deny` | Session | Deny pending device |

### `/device` Page (`apps/web/src/app/(deesse)/device/page.tsx`)

- Display code entry field for user code lookup
- Show device info: client name, IP, timestamp (phishing mitigation)
- Display the exact code user should enter
- Confirm button that redirects to approve

### Anti-Phishing Measures

Per RFC 8628, the verification page MUST show:
- The exact `user_code` the user should type
- Client application name/icon
- Timestamp of request
- Approximate location/IP (if available)

```tsx
// Example: Show device info before approval
<div className="device-info">
  <p>Client: <strong>{clientName}</strong></p>
  <p>Code: <strong>{userCode}</strong></p>
  <p>Location: <strong>{approxLocation}</strong></p>
  <p>Time: <strong>{requestTime}</strong></p>
</div>
```

---

## Security Requirements

### Client Validation

Only pre-registered clients can initiate device flow:

```typescript
validateClient: (clientId) => {
  return ALLOWED_CLIENT_IDS.includes(clientId)
}
```

### Rate Limiting

Apply rate limits to prevent abuse:

| Endpoint | Limit |
|----------|-------|
| `/device/code` | 10 requests/minute per IP |
| `/device/token` | 60 requests/minute per device_code |
| `/device/approve` | 5 attempts/minute per user |
| `/device` | 20 requests/minute per IP |

### Server-Side Revocation

On `fresh auth logout`, the CLI should call a revocation endpoint AND the server should support token revocation:

```typescript
// Server: POST /device/revoke
// Requires session, revokes all device codes for user

// CLI logout should:
// 1. Call revocation endpoint
// 2. Delete local credentials
```

---

## Token Storage

### Structured Credential Format

Store more than just the access token:

```typescript
interface StoredCredential {
  accessToken: string
  refreshToken: string
  expiresAt: number          // Unix timestamp
  scope: string
  accountId: string
  environment: "production" | "staging"
  tokenType: "device_flow"
  issuedAt: number
}
```

### Storage Implementation

```typescript
import keytar from "keytar"

const SERVICE = "fresh-cli"

export async function storeCredential(cred: StoredCredential): Promise<void> {
  await keytar.setPassword(SERVICE, "credential", JSON.stringify(cred))
}

export async function getCredential(): Promise<StoredCredential | null> {
  const raw = await keytar.getPassword(SERVICE, "credential")
  return raw ? JSON.parse(raw) : null
}

export async function deleteCredential(): Promise<void> {
  await keytar.deletePassword(SERVICE, "credential")
}
```

### Refresh Token Support

Design for refresh tokens from the start:

```typescript
export async function refreshAccessToken(): Promise<StoredCredential> {
  const cred = await getCredential()
  if (!cred?.refreshToken) throw new Error("No refresh token")

  const response = await fetch(`${API_BASE}/oauth/token`, {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: cred.refreshToken,
      client_id: "fresh-cli"
    })
  })

  const data = await response.json()
  // Store new credential with updated tokens
  return storeCredential({ ...cred, ...data, issuedAt: Date.now() })
}
```

---

## Database Schema

### Use Plugin-Generated Migration

DO NOT manually create the device_code table. Let Better Auth generate the migration:

```bash
npx drizzle-kit generate
# Review and run the generated migration
```

If custom schema is required (e.g., to add audit fields):

```typescript
// apps/web/src/db/schema/device-code.ts
import { pgTable, text, timestamp } from "drizzle-orm/pg-core"

export const deviceCode = pgTable("device_code", {
  id: text("id").primaryKey(),
  deviceCode: text("device_code").notNull().unique(),
  userCode: text("user_code").notNull().unique(),
  userId: text("user_id").references(() => user.id),
  clientId: text("client_id"),
  scope: text("scope"),
  status: text("status", {
    enum: ["pending", "approved", "denied", "expired"]
  }).notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  lastPolledAt: timestamp("last_polled_at"),
  // Lifecycle timestamps
  approvedAt: timestamp("approved_at"),
  deniedAt: timestamp("denied_at"),
  consumedAt: timestamp("consumed_at"),
  createdAt: timestamp("created_at").defaultNow(),
  // Audit fields
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
}, (table) => ({
  // Indexes
  deviceCodeIdx: unique().on(table.deviceCode),
  userCodeIdx: unique().on(table.userCode),
  statusIdx: index("status_idx").on(table.status),
  expiresIdx: index("expires_idx").on(table.expiresAt),
}))
```

### Cleanup Strategy

Add a scheduled job to:
1. Delete expired device codes (status = "expired")
2. Delete consumed codes older than 24 hours
3. Delete pending codes older than 48 hours

---

## CLI Commands

### Command Structure

```typescript
#!/usr/bin/env node
import { Command } from "commander"

const program = new Command()

program
  .name("fresh")
  .description("Fresh CLI - AI-powered web search and fetch")
  .version("0.1.0")

program
  .command("auth")
  .description("Authentication commands")
  .addCommand(loginCommand)
  .addCommand(logoutCommand)
  .addCommand(statusCommand)
  .addCommand(whoamiCommand)

program.parse()
```

### Commands

| Command | Description |
|---------|-------------|
| `fresh auth login` | Initiate device auth flow |
| `fresh auth logout` | Revoke token and clear credentials |
| `fresh auth status` | Check authentication state |
| `fresh auth whoami` | Show current user info |

### Enhanced `login.ts`

```typescript
export async function login(options: { noOpen?: boolean } = {}): Promise<void> {
  // 1. Request device code using Better Auth client
  const deviceFlow = await client.auth.device.code({
    clientId: "fresh-cli",
    scope: "openid profile offline_access"
  })

  // 2. Display code and URI - show BOTH for resilience
  console.log(bold(`\n  Visit: ${deviceFlow.verificationUriComplete || deviceFlow.verificationUri}`))
  console.log(bold(`  Code:  ${deviceFlow.userCode}\n`))

  // 3. Attempt to open browser, but don't fail if it doesn't work
  if (!options.noOpen) {
    try {
      await open(deviceFlow.verificationUriComplete || deviceFlow.verificationUri)
    } catch {
      console.log("  (Could not open browser automatically)\n")
    }
  }

  // 4. Poll with correct interval handling per RFC 8628
  console.log("  Waiting for authorization...")
  let interval = deviceFlow.interval * 1000

  while (true) {
    const tokenResponse = await client.auth.device.token({
      grantType: "urn:ietf:params:oauth:grant-type:device_code",
      deviceCode: deviceFlow.deviceCode,
      clientId: "fresh-cli"
    })

    if (tokenResponse.error) {
      switch (tokenResponse.error) {
        case "authorization_pending":
          await sleep(interval)
          continue
        case "slow_down":
          interval += 5000  // Increase by 5 seconds per RFC 8628
          await sleep(interval)
          continue
        case "expired_token":
          throw new Error("Code expired. Run 'fresh auth login' to try again.")
        case "access_denied":
          throw new Error("Access denied. Run 'fresh auth login' to try again.")
        default:
          throw new Error(tokenResponse.errorDescription || "Unknown error")
      }
    }

    // 5. Store structured credential
    await storeCredential({
      accessToken: tokenResponse.accessToken,
      refreshToken: tokenResponse.refreshToken ?? "",
      expiresAt: Date.now() + (tokenResponse.expiresIn * 1000),
      scope: tokenResponse.scope,
      accountId: "",  // Will be filled by whoami
      environment: "production",
      tokenType: "device_flow",
      issuedAt: Date.now()
    })

    console.log("\n  Successfully authenticated!")
    return
  }
}
```

### Enhanced `status.ts`

```typescript
export async function status(): Promise<void> {
  const cred = await getCredential()

  if (!cred) {
    console.log("Not authenticated. Run 'fresh auth login' to login.")
    return
  }

  const now = Date.now()
  if (cred.expiresAt < now) {
    console.log("Token expired. Run 'fresh auth login' to re-authenticate.")
    return
  }

  console.log(`Authenticated`)
  console.log(`Expires: ${new Date(cred.expiresAt).toLocaleString()}`)
  console.log(`Environment: ${cred.environment}`)
}
```

### Enhanced `whoami.ts`

```typescript
export async function whoami(): Promise<void> {
  const cred = await getCredential()
  if (!cred) {
    console.log("Not authenticated.")
    return
  }

  try {
    const userInfo = await fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${cred.accessToken}` }
    }).then(r => r.json())

    console.log(`User: ${userInfo.name} (${userInfo.email})`)
    console.log(`Account ID: ${userInfo.id}`)
  } catch (error) {
    console.error("Failed to fetch user info:", error.message)
  }
}
```

---

## Error Handling

| Error | User Message | Recovery |
|-------|--------------|----------|
| `authorization_pending` | "Waiting for approval..." | Continue polling with same interval |
| `slow_down` | "Polling too fast, slowing down..." | Increase interval by 5s |
| `expired_token` | "Code expired. Run 'fresh auth login' to try again." | Restart flow |
| `access_denied` | "Access denied. Run 'fresh auth login' to try again." | Restart flow |
| `network_error` | "Network error. Check your connection." | Retry with exponential backoff |
| `browser_open_failed` | "(Could not open browser - visit URL manually)" | Show URL, continue |
| `keychain_error` | "Failed to store credentials securely." | Report and exit |

### CLI Flags

```bash
fresh auth login --no-open    # Don't attempt to open browser
fresh auth login --json       # JSON output for scripting
fresh auth login --debug      # Debug output
```

---

## Testing Requirements

### RFC Behavior Tests

Test all RFC 8628 error handling:

```typescript
// tests/rfc.spec.ts
test("slow_down increases interval by 5 seconds", async () => {
  let callCount = 0
  let usedInterval = 5000

  mock.onPost("/device/token").reply(() => {
    callCount++
    if (callCount === 1) {
      return { error: "slow_down" }
    }
    return { access_token: "token" }
  })

  await pollForToken("device_code", 5)

  // Should have increased interval by 5s on slow_down
  expect(usedInterval).toBe(10000) // 5000 + 5000
})

test("expires_in handles expiry", async () => {
  mock.onPost("/device/token").reply({
    error: "expired_token"
  })

  await expect(pollForToken("device_code", 5)).rejects.toThrow("expired")
})
```

### Security Tests

```typescript
// tests/security.spec.ts
test("rate limiting prevents brute force", async () => {
  // Make 11 requests to /device/approve
  for (let i = 0; i < 11; i++) {
    const res = await post("/device/approve", invalidData)
    if (i >= 10) {
      expect(res.status).toBe(429)
    }
  }
})

test("unregistered client cannot initiate flow", async () => {
  const res = await post("/device/code", { client_id: "evil-client" })
  expect(res.status).toBe(400)
})
```

### End-to-End Tests

```typescript
// tests/e2e.spec.ts
test("cli token can call protected API", async () => {
  // 1. Login via device flow
  await fresh("auth login --no-open")

  // 2. Call protected endpoint
  const result = await fresh("search --query 'test'")

  // 3. Verify result
  expect(result.ok).toBe(true)
})

test("logout revokes server-side token", async () => {
  // 1. Login
  await fresh("auth login")

  // 2. Verify token works
  const before = await fresh("auth whoami")
  expect(before.ok).toBe(true)

  // 3. Logout
  await fresh("auth logout")

  // 4. Verify token revoked on server
  const after = await fresh("auth whoami")
  expect(after.ok).toBe(false)
})
```

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `apps/cli/package.json` | Create | CLI package |
| `apps/cli/tsconfig.json` | Create | TypeScript config |
| `apps/cli/src/index.ts` | Create | CLI entry point |
| `apps/cli/src/commands/auth/login.ts` | Create | Device auth flow |
| `apps/cli/src/commands/auth/logout.ts` | Create | Revocation + cleanup |
| `apps/cli/src/commands/auth/status.ts` | Create | Show auth state |
| `apps/cli/src/commands/auth/whoami.ts` | Create | Show user info |
| `apps/cli/src/commands/auth/index.ts` | Create | Command registration |
| `apps/cli/src/lib/client.ts` | Create | Better Auth client wrapper |
| `apps/cli/src/lib/storage.ts` | Create | Structured credential storage |
| `apps/cli/src/lib/config.ts` | Create | Config with profiles |
| `apps/cli/src/utils/open.ts` | Create | Cross-platform browser open |
| `apps/web/src/deesse.config.ts` | Modify | Add deviceAuthorization plugin (NOT lib/deesse.ts) |
| `apps/web/src/app/(deesse)/device/page.tsx` | Create | Code entry + confirmation |
| `apps/web/src/app/api/device/approve/route.ts` | Create | Approval endpoint |
| `apps/web/src/app/api/device/deny/route.ts` | Create | Denial endpoint |
| `apps/web/src/app/api/device/revoke/route.ts` | Create | Revocation endpoint |
| `migrations/*` | Create | Device code table migration |

---

## Environment Variables

| Variable | CLI | Server | Description |
|----------|-----|--------|-------------|
| `FRESH_API_URL` | Yes | No | CLI base URL |
| `AUTH_BASE_URL` | No | Yes | Server auth base URL |
| `ALLOWED_DEVICE_CLIENTS` | No | Yes | Comma-separated client IDs |

---

## Security Considerations

1. **OS Keychain Storage**: `keytar` handles cross-platform secure storage
2. **No Password Exposure**: Users never type credentials
3. **Client Validation**: Only registered clients can initiate device flow
4. **Rate Limiting**: Prevent brute force on user codes
5. **Phishing Mitigation**: Show device info on approval page
6. **Server-Side Revocation**: Tokens can be revoked on logout
7. **Structured Credentials**: Store metadata for refresh/expiry handling

---

## Implementation Phases

### Phase 1: Server-Side
- Add deviceAuthorization plugin to deesse.config.ts
- Create /device, /device/approve, /device/deny, /device/revoke routes
- Generate and run database migration
- Add rate limiting middleware

### Phase 2: CLI Core
- Create apps/cli package structure
- Implement Better Auth client wrapper
- Implement structured credential storage
- Implement login command with RFC 8628 compliance

### Phase 3: CLI Commands
- Implement logout with server-side revocation
- Implement status with expiry check
- Implement whoami with user info fetch

### Phase 4: Polish
- Add `--no-open`, `--json`, `--debug` flags
- Add multi-environment profiles
- Add spinner and progress indicators
- Comprehensive test coverage
