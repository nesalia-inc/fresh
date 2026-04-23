# Better Auth - Learning Notes

This directory contains learning documents for better-auth plugins and features.

## Documents

1. [API Key Plugin](./api-key.md) - Create, manage, verify API keys with rate limiting, remaining counts, and permissions
2. [2FA Plugin](./2fa.md) - Two-factor authentication with TOTP, OTP, backup codes, and trusted devices

## Key Concepts

| Concept | Description |
|---------|-------------|
| **API Key plugin** | Authentication via static keys with built-in rate limiting |
| **2FA plugin** | Two-factor authentication (TOTP, OTP, backup codes) |
| **Stripe plugin** | Subscription billing with plan limits |
| **Device Authorization** | OAuth-like flow for CLI/device apps |

## Quick Reference

```typescript
// API Key Setup
import { apiKey } from "@better-auth/api-key";
export const auth = betterAuth({
  plugins: [apiKey()]
});

// 2FA Setup
import { twoFactor } from "@better-auth/plugins";
export const auth = betterAuth({
  appName: "My App",
  plugins: [twoFactor()]
});
```

## Resources

- [better-auth.com](https://better-auth.com)
- [API Key Plugin Docs](https://better-auth.com/docs/plugins/api-key)
- [2FA Plugin Docs](https://better-auth.com/docs/plugins/2fa)
- [Stripe Plugin Docs](https://better-auth.com/docs/plugins/stripe)
