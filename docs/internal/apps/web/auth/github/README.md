# GitHub Authentication

Social sign-in with GitHub OAuth.

## Overview

Fresh supports GitHub OAuth for developers to sign in using their GitHub accounts. This is ideal for developer-focused products and teams.

## How It Works

1. User clicks "Sign in with GitHub"
2. Redirect to GitHub's authorization page
3. User grants permissions
4. Redirect back to Fresh with auth code
5. Session established, user is logged in

## Configuration

### Environment Variables

```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### GitHub Developer Portal Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new **OAuth App**
3. Fill in application details:
   - **Application name**: Fresh
   - **Homepage URL**: `https://fresh.dev`
   - **Authorization callback URL**:
     - Local: `http://localhost:3000/api/auth/callback/github`
     - Production: `https://api.fresh.dev/api/auth/callback/github`

### Server Setup

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
    socialProviders: {
        github: {
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET,
        },
    },
})
```

## Important: Email Scope

You **must** include the `user:email` scope, or you'll get an `email_not_found` error.

For GitHub Apps:
1. Go to **Permissions and Events** → **Account Permissions** → **Email Addresses**
2. Select **Read-Only**

## Client Usage

### Web SDK

```typescript
import { createAuthClient } from "better-auth/client"

const authClient = createAuthClient()

const signIn = async () => {
    const data = await authClient.signIn.social({
        provider: "github"
    })
    console.log(data.user)
}
```

### React Component

```tsx
import { SignInButton } from '@fresh/react/auth'

export function LoginPage() {
  return (
    <div>
      <h1>Sign in to Fresh</h1>
      <SignInButton provider="github" />
    </div>
  )
}
```

## Important Notes

### No Refresh Tokens

GitHub doesn't issue refresh tokens. Access tokens remain valid indefinitely unless:
- User revokes access
- App is deleted
- Token unused for 1 year

No refresh token handling is needed.

### Token Storage

Access tokens are stored server-side in the session. The client only receives session cookies.

## Database Schema

### User Table Additions

```typescript
interface User {
    // ... other fields
    githubId?: string;
    email?: string;
    name?: string;
    username?: string;    // GitHub username
    image?: string;      // Avatar URL
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign-in/github` | GET | Initiate GitHub OAuth flow |
| `/callback/github` | GET | OAuth callback |
| `/sign-out` | POST | Sign out user |

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `email_not_found` | Missing `user:email` scope | Add email scope in GitHub App settings |
| `redirect_uri_mismatch` | Wrong callback URL | Check GitHub App callback URL |
| `access_denied` | User denied permission | User must grant access |

## Related

- [Google](../google/README) - Google OAuth
- [Email/Password](../email-password/README) - Email/password authentication
- [API Key](../../packages/sdk/README) - API key authentication
