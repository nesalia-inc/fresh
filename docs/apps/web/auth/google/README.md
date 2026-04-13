# Google Authentication

Social sign-in with Google OAuth 2.0.

## Overview

Fresh supports Google OAuth for seamless authentication. Users can sign in with their Google account without creating a new password.

## How It Works

1. User clicks "Sign in with Google"
2. Redirect to Google's consent screen
3. User grants permissions
4. Redirect back to Fresh with auth code
5. Session established, user is logged in

## Configuration

### Environment Variables

```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
BETTER_AUTH_URL=https://api.fresh.dev
```

### Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services** → **Credentials**
4. Create **OAuth client ID**
5. Set application type to **Web application**
6. Add authorized redirect URIs:
   - Local: `http://localhost:3000/api/auth/callback/google`
   - Production: `https://api.fresh.dev/api/auth/callback/google`

### Server Setup

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
    baseURL: process.env.BETTER_AUTH_URL,
    socialProviders: {
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        },
    },
})
```

## Client Usage

### Web SDK

```typescript
import { createAuthClient } from "better-auth/client"

const authClient = createAuthClient()

// Sign in with redirect
await authClient.signIn.social({ provider: "google" })

// Sign in with ID token (no redirect)
await authClient.signIn.social({
    provider: "google",
    idToken: {
        token: "google-id-token",
        accessToken: "google-access-token"
    }
})
```

### React Component

```tsx
import { SignInButton } from '@fresh/react/auth'

export function LoginPage() {
  return (
    <div>
      <h1>Sign in to Fresh</h1>
      <SignInButton provider="google" />
    </div>
  )
}
```

## Options

### Sign-In Options

| Option | Type | Description |
|--------|------|-------------|
| `prompt` | `string` | `"select_account"` to always show account picker |
| `accessType` | `string` | `"offline"` to get refresh tokens |
| `scopes` | `string[]` | Additional Google scopes |

### Refresh Tokens

To get refresh tokens for offline access:

```typescript
await authClient.signIn.social({
    provider: "google",
    accessType: "offline",
    prompt: "select_account consent"
})
```

### Additional Scopes

```typescript
await authClient.signIn.social({
    provider: "google",
    scopes: ["https://www.googleapis.com/auth/drive.readonly"]
})
```

## Database Schema

### User Table Additions

```typescript
interface User {
    // ... other fields
    googleId?: string;
    email?: string;
    name?: string;
    image?: string;
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign-in/google` | GET | Initiate Google OAuth flow |
| `/callback/google` | GET | OAuth callback |
| `/sign-out` | POST | Sign out user |

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `redirect_uri_mismatch` | Wrong callback URL | Check Google Cloud Console redirect URIs |
| `access_denied` | User denied permission | User must grant access |
| `id_token_invalid` | Invalid ID token | Refresh token may be expired |

## Related

- [GitHub](../github/README) - GitHub OAuth
- [Email/Password](../email-password/README) - Email/password authentication
- [API Key](../../packages/sdk/README) - API key authentication
