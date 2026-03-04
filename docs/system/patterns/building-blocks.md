# Common Building Blocks

90% of software uses the same building blocks.

## The 90% Problem

Every software project uses these common blocks:

```
DATABASE              CACHE               AUTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- CRUD              - Redis           - Login
- Migrations        - Memcached       - OAuth
- Queries           - CDN             - SSO
- Relations         - HTTP cache      - API keys

PAYMENTS             QUEUES             SEARCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Stripe            - RabbitMQ        - Algolia
- PayPal            - SQS             - MeiliSearch
- Wallet            - Redis           - Elastic
- Subscriptions     - BullMQ          - Typesense

PERMISSIONS          EMAIL              UPLOAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- RBAC              - SendGrid        - S3
- ABAC              - AWS SES         - Cloudinary
- Policies          - Resend          - Local
- Teams             - Templates       - Streaming
```

## Each Block Has Common Patterns

Example: PAYMENTS

```
Payment Flow:
Create Intent → Verify → Process → Confirm & Notify

Refund Flow:
Request → Verify Eligibility → Process Refund

Webhook Handling:
Receive → Verify Signature → Process Event

Error Handling:
Declined → User message
Network error → Retry with backoff
Webhook failed → Queue for retry
Fraud → Block & alert
```

Edge Cases:
- Duplicate payments → Idempotency keys
- Partial refunds → Track remaining amount
- Currency conversion → Use exact amounts
- 3DS failure → Clear error message

---

*Last updated: 2026-03-04*
