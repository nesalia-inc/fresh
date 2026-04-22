# Fresh Payments

Subscription management powered by Stripe for Fresh web application.

## Overview

Fresh uses Stripe for subscription billing. Users can upgrade to Pro/Enterprise plans, manage their billing, and handle cancellations through an integrated billing portal.

## Pricing Plans

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | 100 requests/hour, basic search |
| **Pro** | $29/month | 1,000 requests/hour, deep research, streaming |
| **Enterprise** | Custom | Unlimited, dedicated support, custom limits |

### Plan Limits

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Requests/hour | 100 | 1,000 | Unlimited |
| Search | ✓ | ✓ | ✓ |
| Fetch | ✓ | ✓ | ✓ |
| Ask | - | ✓ | ✓ |
| Research | - | ✓ | ✓ |
| Streaming | - | ✓ | ✓ |
| Deep reasoning | - | ✓ | ✓ |
| Team seats | - | 5 | Unlimited |
| Priority support | - | - | ✓ |
| Custom rate limits | - | - | ✓ |

## CLI Integration

### fresh api-key list

List your API keys with usage and billing info:

```bash
$ fresh api-key list
ID          | Name       | Expires   | Last Used
key_abc123  | Development | 30d       | 2h ago
key_def456  | Production  | 90d       | 5m ago
```

### fresh api-key create

Create a new API key:

```bash
# Basic key
fresh api-key create --name "My App"

# With expiration
fresh api-key create --name "Temp Key" --expires-in 7d

# Team/organization key
fresh api-key create --name "Team Key" --org "org_123" --seats 5
```

## API Endpoints

### POST /subscription/upgrade

Create or upgrade a subscription.

**Request:**

```json
{
  "plan": "pro",
  "successUrl": "/dashboard?success=true",
  "cancelUrl": "/pricing?cancelled=true",
  "annual": false
}
```

**Response:**

```json
{
  "checkoutUrl": "https://billing.stripe.com/..."
}
```

### GET /subscription/list

List subscriptions for a user or organization.

**Response:**

```json
{
  "subscriptions": [
    {
      "id": "sub_abc123",
      "plan": "pro",
      "status": "active",
      "periodStart": "2025-03-01T00:00:00Z",
      "periodEnd": "2025-04-01T00:00:00Z",
      "cancelAtPeriodEnd": false,
      "seats": 1,
      "billingInterval": "month"
    }
  ]
}
```

### POST /subscription/cancel

Cancel a subscription (redirects to Stripe Billing Portal).

**Request:**

```json
{
  "subscriptionId": "sub_abc123",
  "returnUrl": "/account"
}
```

### POST /subscription/restore

Undo a pending cancellation or scheduled plan change.

**Request:**

```json
{
  "subscriptionId": "sub_abc123"
}
```

### POST /subscription/billing-portal

Open Stripe Billing Portal for self-service management.

**Request:**

```json
{
  "returnUrl": "/account"
}
```

**Response:**

```json
{
  "url": "https://billing.stripe.com/..."
}
```

## Web Dashboard

### Subscription Page

Users can view and manage their subscription from the web dashboard:

```
/dashboard/subscription
```

Features:
- View current plan and usage
- Upgrade/downgrade plan
- Cancel subscription
- Update payment method
- Download invoices
- Manage team seats

### Usage Dashboard

Real-time usage metrics:

```
/dashboard/usage
```

Metrics:
- Requests this hour/month
- API calls breakdown (search, fetch, ask, research)
- Cost tracking
- Usage graphs

## Database Schema

### Subscription Table

```typescript
interface Subscription {
  id: string;
  plan: 'free' | 'pro' | 'enterprise';
  referenceId: string;           // User ID or Org ID
  stripeCustomerId?: string;
  stripeSubscriptionId?: string;
  status: 'active' | 'trialing' | 'canceled' | 'past_due' | 'unpaid';
  periodStart?: Date;
  periodEnd?: Date;
  cancelAtPeriodEnd?: boolean;
  cancelAt?: Date;
  canceledAt?: Date;
  endedAt?: Date;
  seats?: number;
  trialStart?: Date;
  trialEnd?: Date;
  billingInterval?: 'month' | 'year';
  stripeScheduleId?: string;      // For scheduled plan changes
}
```

### User Table Additions

```typescript
interface User {
  // ... other fields
  stripeCustomerId?: string;
}
```

## Stripe Webhook Events

Fresh handles these Stripe webhook events:

| Event | Handler |
|-------|---------|
| `checkout.session.completed` | Update subscription after checkout |
| `customer.subscription.created` | Create subscription record |
| `customer.subscription.updated` | Sync plan/status changes |
| `customer.subscription.deleted` | Mark subscription as canceled |
| `invoice.paid` | Extend subscription period |
| `invoice.payment_failed` | Mark subscription as past_due |

### Webhook URL

```
https://api.fresh.dev/stripe/webhook
```

### Local Testing

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

## Client Integration

### SDK Usage

```typescript
import { createClient } from '@fresh/sdk';

const client = createClient({
  apiKey: 'fresh_sk_your-api-key'
});

// Check subscription status
const subscription = await client.getSubscription();
console.log(subscription.plan); // 'pro'
console.log(subscription.status); // 'active'

// Get usage
const usage = await client.getUsage();
console.log(usage.requestsThisHour); // 45
console.log(usage.limits.requestsPerHour); // 1000
```

### React Components

```tsx
import { SubscriptionProvider, useSubscription } from '@fresh/react';

function BillingPage() {
  const { subscription, isLoading } = useSubscription();

  if (isLoading) return <Loading />;

  return (
    <div>
      <h1>Current Plan: {subscription.plan}</h1>
      <UpgradeButton plan="pro" />
      <ManageBillingButton />
    </div>
  );
}
```

## Rate Limits by Plan

| Plan | Search | Fetch | Ask | Research |
|------|--------|-------|-----|----------|
| Free | 100/hr | 100/hr | - | - |
| Pro | 1,000/hr | 1,000/hr | 100/hr | 10/hr |
| Enterprise | Custom | Custom | Custom | Custom |

Rate limits are tracked via Stripe's metered billing and refreshed hourly.

## Error Handling

### Payment Errors

```typescript
try {
  await client.subscribe('pro');
} catch (error) {
  if (error.code === 'PAYMENT_FAILED') {
    // Handle failed payment
    console.error('Payment failed:', error.message);
  } else if (error.code === 'SUBSCRIPTION_LIMITED') {
    // User already has active subscription
    console.error('Already subscribed');
  }
}
```

### Webhook Failures

If webhook processing fails, Stripe will retry with exponential backoff. Critical failures are logged and alert the team.

## Testing

### Stripe Test Mode

Use Stripe test mode keys for development:

```typescript
const stripeClient = new Stripe('sk_test_...', {
  apiVersion: '2024-12-18.acacia'
});
```

### Test Cards

```typescript
// Successful payment
{ card: '4242424242424242' }

// Requires authentication
{ card: '4000002500003155' }

// Payment declined
{ card: '4000000000000002' }
```

## Related

- [CLI](../cli/README) - CLI authentication and API key management
- [SDK](../../packages/sdk/README) - SDK with subscription methods
