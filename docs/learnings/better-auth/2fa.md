# Two-Factor Authentication (2FA) Plugin

## Overview

The 2FA plugin adds an extra security layer for user authentication. Users need a second form of verification beyond their password.

## Features

| Feature | Description |
|---------|-------------|
| **TOTP** | Time-based codes from authenticator apps (Google Auth, etc.) |
| **OTP** | One-time codes sent via email/phone |
| **Backup Codes** | Recovery codes when 2FA device is unavailable |
| **Trusted Devices** | Remember devices for 30 days |
| **Passkey Support** | Can work without password |

---

## Installation

### Server Setup

```typescript
// auth.ts
import { betterAuth } from "better-auth"
import { twoFactor } from "@better-auth/plugins"

export const auth = betterAuth({
  appName: "My App",  // Used as TOTP issuer
  plugins: [
    twoFactor()
  ]
})
```

### Client Setup

```typescript
// auth-client.ts
import { createAuthClient } from "better-auth/client"
import { twoFactorClient } from "@better-auth/client/plugins"

export const authClient = createAuthClient({
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect({ twoFactorMethods }) {
        // Redirect to 2FA verification page
        window.location.href = "/two-factor"
      }
    })
  ]
})
```

### Database Migration

```bash
npx auth migrate
```

---

## User Flow

```
1. User signs in with email + password
2. If 2FA enabled → response.twoFactorRedirect = true
3. User redirected to 2FA page
4. User enters TOTP/OTP code
5. Code verified → session created
6. If trustDevice=true → device remembered for 30 days
```

---

## TOTP (Time-Based OTP)

### What is TOTP?

- Codes generated offline by authenticator apps
- New code every 30 seconds
- No SMS/email delivery risk
- Most secure option

### Enable 2FA with TOTP

```typescript
// Client
const { data, error } = await authClient.twoFactor.enable({
  password: "user-password",
  issuer: "My App"  // Optional, defaults to appName
});

// Returns: { totpURI, backupCodes }
// Show QR code from totpURI for user to scan
```

### Get TOTP URI (QR Code)

```typescript
// Client
const { data } = await authClient.twoFactor.getTotpUri({
  password: "user-password"
});

// data.totpURI → "otpauth://totp/My App:user@example.com?secret=XXX&issuer=My+App"

// Display QR code
import QRCode from "react-qr-code";

<QRCode value={data?.totpURI || ""} />
```

### Verify TOTP

```typescript
// Client
const { data, error } = await authClient.twoFactor.verifyTotp({
  code: "123456",       // 6-digit code
  trustDevice: true      // Remember for 30 days
});

if (data) {
  // 2FA verified successfully
}
```

---

## OTP (One-Time Password via Email/SMS)

### What is OTP?

- Random code sent to email or phone
- User must receive and enter code
- Requires `sendOTP` configuration

### Configure sendOTP

```typescript
// auth.ts
export const auth = betterAuth({
  plugins: [
    twoFactor({
      otpOptions: {
        async sendOTP({ user, otp }, ctx) {
          // Send OTP via email, SMS, etc.
          await sendEmail({
            to: user.email,
            subject: "Your 2FA Code",
            text: `Your code is: ${otp}`
          })
        }
      }
    })
  ]
})
```

### Send OTP

```typescript
// Client
const { data } = await authClient.twoFactor.sendOtp({
  trustDevice: true
});

if (data) {
  // OTP sent, show input field to user
}
```

### Verify OTP

```typescript
// Client
const { data, error } = await authClient.twoFactor.verifyOtp({
  code: "123456",
  trustDevice: true
});
```

---

## Backup Codes

### Generate Backup Codes

```typescript
// Client
const { data } = await authClient.twoFactor.generateBackupCodes({
  password: "user-password"
});

if (data) {
  // data.backupCodes = ["123456", "789012", ...]
  // SHOW THESE TO USER - they only appear once!
}
```

### Verify with Backup Code

```typescript
// Client
const { data } = await authClient.twoFactor.verifyBackupCode({
  code: "123456",
  disableSession: false,  // Set session cookie
  trustDevice: true       // Remember device
});
```

> Once used, a backup code is deleted and cannot be reused.

### View Backup Codes

```typescript
// Server only - for displaying to user
const data = await auth.api.viewBackupCodes({
  body: { userId: "user-id" }
});
// Returns: { backupCodes: [...] }
```

---

## Trusted Devices

### How It Works

- When `trustDevice: true` → device remembered for 30 days
- During this period, no 2FA prompt on that device
- Trust refreshed on each successful sign-in

```typescript
// Any verification with trustDevice
await authClient.twoFactor.verifyTotp({
  code: "123456",
  trustDevice: true
});
```

---

## Disable 2FA

```typescript
// Client
const { data } = await authClient.twoFactor.disable({
  password: "user-password"
});
```

---

## Sign In Flow with 2FA

```typescript
// Client
await authClient.signIn.email({
  email: "user@example.com",
  password: "password123"
}, {
  async onSuccess(context) {
    if (context.data.twoFactorRedirect) {
      // context.data.twoFactorMethods = ["totp"] or ["totp", "otp"]
      // Redirect to 2FA verification page
      router.push("/two-factor-verify");
    } else {
      // Normal login success
      router.push("/dashboard");
    }
  }
})
```

### Server-Side

```typescript
// Server
const { headers: responseHeaders, response } = await auth.api.signInEmail({
  returnHeaders: true,
  body: { email, password }
});

if ("twoFactorRedirect" in response) {
  // User has 2FA enabled
  // response.twoFactorMethods tells us what methods are available
  // Must forward cookies: headers: responseHeaders
}
```

---

## Schema

### Additional User Field

```typescript
// user table
twoFactorEnabled: boolean  // Optional
```

### twoFactor Table

```typescript
// twoFactor table
{
  id: string,           // PK
  userId: string,       // FK to user
  secret: string,       // Encrypted TOTP secret
  backupCodes: string,  // Hashed backup codes
  verified: boolean     // Has user verified during enrollment?
}
```

---

## Options

### Server Options

```typescript
twoFactor({
  twoFactorTable: "twoFactor",           // Table name
  skipVerificationOnEnable: false,       // Skip verification step
  allowPasswordless: true,              // Allow without password (passkeys, OAuth)
  issuer: "My App",                      // TOTP issuer name

  // TOTP options
  totpOptions: {
    digits: 6,        // Code length (default 6)
    period: 30,      // Seconds per code (default 30)
  },

  // OTP options
  otpOptions: {
    sendOTP: async ({ user, otp }) => { /* send it */ },
    period: 300,     // Expiry in seconds
  },

  // Backup codes
  backupCodes: {
    amount: 10,       // Number of codes
    length: 6,       // Code length
  }
})
```

### Client Options

```typescript
twoFactorClient({
  onTwoFactorRedirect({ twoFactorMethods }) {
    // e.g. ["totp"] or ["totp", "otp"]
    window.location.href = "/2fa";
  }
})
```

---

## Use Cases for fresh-final

### 1. Secure CLI Authentication

For sensitive operations, require 2FA:

```typescript
// Server middleware for sensitive commands
if (command.requires2FA && !session.user.twoFactorEnabled) {
  throw new Error("2FA required for this operation");
}
```

### 2. Organization Security

Team/org owners can enforce 2FA for all members:

```typescript
// Org settings
orgSettings.require2FA = true;
```

### 3. API Key + 2FA

Combine API keys with 2FA for high-security API access:

```typescript
// Create API key that requires 2FA to use
const { data } = await auth.api.createApiKey({
  body: {
    name: "secure-key",
    userId: "user-id",
    permissions: { admin: ["full"] },
    twoFactorRequired: true  // Custom metadata flag
  }
});
```

---

## Resources

- [Official Documentation](https://better-auth.com/docs/plugins/2fa)
- [TOTP Standard](https://en.wikipedia.org/wiki/Time-based_one-time_password)
- [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) - TOTP specification
