# Pattern Extraction Philosophy

A pragmatic approach to building quality software through iterative analysis of real code, understanding fundamental building blocks, and designing for evolution.

---

## The Core Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE PRAGMATIC APPROACH                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Don't try to define "good" theoretically                      │
│                                                                 │
│   INSTEAD:                                                      │
│                                                                 │
│   1. Take real code                                            │
│   2. Analyze it deeply                                          │
│   3. Identify what's good                                        │
│   4. Identify what's bad                                         │
│   5. Extract the pattern                                         │
│   6. Iterate and improve                                         │
│                                                                 │
│   Patterns emerge from ANALYSIS, not specification              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: The Pattern Extraction Process

### Step-by-Step

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATTERN EXTRACTION WORKFLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │ 1. Collect   │ ← Take real code from real projects        │
│   │ Real Code    │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ 2. Analyze   │ ← Deep dive into each piece               │
│   │ Deeply       │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ 3. Extract   │ ← What works? What doesn't?               │
│   │ Patterns     │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ 4. Abstract │ ← Create reusable patterns                │
│   │ Patterns     │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ 5. Test in   │ ← Apply to new code                        │
│   │ Real Context │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐                                              │
│   │ 6. Iterate  │ ← Refine based on experience              │
│   │ & Improve   │                                              │
│   └──────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example: Authentication Pattern

```
Let's extract the authentication pattern:

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Collect Real Code                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Project A: Simple JWT auth                                       │
│ - login(username, password) → token                            │
│ - middleware checks token                                      │
│ - token expires after 1 hour                                   │
│                                                                 │
│ Project B: OAuth + JWT                                          │
│ - OAuth2 flow with Google, GitHub                              │
│ - JWT with refresh tokens                                      │
│ - Token rotation                                                │
│                                                                 │
│ Project C: Enterprise auth                                       │
│ - SSO with SAML                                                 │
│ - JWT + refresh tokens                                          │
│ - Session management                                            │
│ - 2FA support                                                   │
│                                                                 │
│ Project D: API keys + JWT                                       │
│ - JWT for users, API keys for services                         │
│ - Scoped permissions                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Analyze Deeply                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ What's COMMON across all:                                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━                                       │
│ - Need to identify user (token, session, key)                  │
│ - Need to verify identity (signature, validation)              │
│ - Need to check permissions (role, scope)                      │
│ - Need to handle expiration (refresh, re-login)                │
│                                                                 │
│ What's DIFFERENT:                                               │
│ ━━━━━━━━━━━━━━━━━━━                                            │
│ - How tokens are issued (JWT, session, SAML, OAuth)            │
│ - How identity is verified (stateless, stateful)              │
│ - How permissions are scoped (roles, scopes, claims)          │
│ - How sessions are managed (cookie, header, token)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3-4: Extract & Abstract Patterns                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ AUTHENTICATION PATTERN (abstracted)                      │  │
│ │                                                           │  │
│ │  ┌─────────────┐                                         │  │
│ │  │ Token Issuer│ ────▶ Issue credential                  │  │
│ │  └──────┬──────┘                                         │  │
│ │         │                                                 │  │
│ │         ▼                                                 │  │
│ │  ┌─────────────┐                                         │  │
│ │  │ Credential │ ────▶ Store securely                     │  │
│ │  │ Storage    │      (httpOnly cookie, secure storage)  │  │
│ │  └──────┬──────┘                                         │  │
│ │         │                                                 │  │
│ │         ▼                                                 │  │
│ │  ┌─────────────┐                                         │  │
│ │  │ Credential │ ────▶ Verify on each request            │  │
│ │  │ Verifier   │      (signature, expiry, revocation)    │  │
│ │  └──────┬──────┘                                         │  │
│ │         │                                                 │  │
│ │         ▼                                                 │  │
│ │  ┌─────────────┐                                         │  │
│ │  │ Permission  │ ────▶ Check access rights              │  │
│ │  │ Checker    │      (roles, scopes, policies)         │  │
│ │  └─────────────┘                                         │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ This pattern can be implemented with:                           │
│ - JWT + middleware                                             │
│ - Session + cookies                                            │
│ - OAuth2 + JWT                                                 │
│ - API keys + permissions                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 2: The 90% Problem

### Common Building Blocks

```
┌─────────────────────────────────────────────────────────────────┐
│                    90% OF SOFTWARE IS BUILTON BLOCKS                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Every software project uses these:                             │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │   DATABASE  │  │    CACHE    │  │    AUTH     │           │
│   │             │  │             │  │             │           │
│   │ - CRUD      │  │ - Redis     │  │ - Login     │           │
│   │ - Migrations│  │ - Memcached │  │ - OAuth     │           │
│   │ - Queries   │  │ - CDN       │  │ - SSO       │           │
│   │ - Relations │  │ - HTTP cache│  │ - API keys  │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │  PAYMENTS   │  │  QUEUES     │  │    SEARCH   │           │
│   │             │  │             │  │             │           │
│   │ - Stripe    │  │ - RabbitMQ  │  │ - Algolia   │           │
│   │ - PayPal    │  │ - SQS       │  │ - MeiliSearch│          │
│   │ - Wallet    │  │ - Redis     │  │ - Elastic   │           │
│   │ - Subscript │  │ - BullMQ    │  │ - Typesense │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │PERMISSIONS  │  │    EMAIL    │  │   UPLOAD    │           │
│   │             │  │             │  │             │           │
│   │ - RBAC      │  │ - SendGrid  │  │ - S3        │           │
│   │ - ABAC      │  │ - AWS SES   │  │ - Cloudinary│           │
│   │ - Policies  │  │ - Resend    │  │ - Local     │           │
│   │ - Teams     │  │ - Templates │  │ - Streaming │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │NOTIFICATIONS│  │    LMS      │  │    CMS      │           │
│   │             │  │             │  │             │           │
│   │ - In-app    │  │ - Courses   │  │ - Content   │           │
│   │ - Email     │  │ - Progress  │  │ - Media     │           │
│   │ - Push      │  │ - Quizzes   │  │ - Versioning│           │
│   │ - SMS       │  │ - Certifs   │  │ - Workflow  │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Each Block Has Common Patterns

```
Example: PAYMENTS Block
━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│ COMMON PAYMENT PATTERNS                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Payment Flow:                                                   │
│ ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│ │ Create  │───▶│ Verify   │───▶│ Process  │───▶│ Confirm  │  │
│ │ Intent  │    │ Payment  │    │ Payment  │    │ & Notify │  │
│ └─────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                 │
│ Refund Flow:                                                    │
│ ┌─────────┐    ┌──────────┐    ┌──────────┐                   │
│ │ Request │───▶│ Verify   │───▶│ Process  │                   │
│ │ Refund  │    │ Eligibility│   │ Refund   │                   │
│ └─────────┘    └──────────┘    └──────────┘                   │
│                                                                 │
│ Webhook Handling:                                               │
│ ┌─────────┐    ┌──────────┐    ┌──────────┐                   │
│ │ Receive │───▶│ Verify   │───▶│ Process  │                   │
│ │ Event   │    │ Signature│    │ Event    │                   │
│ └─────────┘    └──────────┘    └──────────┘                   │
│                                                                 │
│ Error Handling:                                                 │
│ - Payment declined → Show user message                         │
│ - Network error → Retry with backoff                          │
│ - Webhook failed → Queue for retry                            │
│ - Fraud detected → Block & alert                              │
│                                                                 │
│ Edge Cases:                                                    │
│ - Duplicate payments → Idempotency keys                       │
│ - Partial refunds → Track remaining amount                    │
│ - Currency conversion → Use exact amounts                     │
│ - 3DS failure → Clear error message                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Evolution-Aware Development

### The Key Insight

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODE MUST EVOLVE                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   90% of features will change:                                   │
│                                                                 │
│   - New payment provider                                        │
│   - New authentication method                                    │
│   - New cache strategy                                          │
│   - New search engine                                           │
│   - New queue system                                            │
│                                                                 │
│   Good code anticipates this                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Evolution Pattern: Payments

```
BEFORE (not evolution-aware):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│ class PaymentService {                                          │
│   async pay(amount: number) {                                   │
│     const stripe = new Stripe(API_KEY);                        │
│     return await stripe.charges.create({ amount });            │
│   }                                                             │
│ }                                                               │
│                                                                 │
│ Problem: When we add PayPal, we need to rewrite this          │
└─────────────────────────────────────────────────────────────────┘

AFTER (evolution-aware):
━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────┐
│ interface PaymentProvider {                                     │
│   createPayment(amount: number, currency: string): Payment;    │
│   verifyPayment(id: string): boolean;                          │
│   refundPayment(id: string): Refund;                          │
│ }                                                               │
│                                                                  │
│ class StripeProvider implements PaymentProvider {               │
│   createPayment(amount, currency) {                            │
│     return new StripePayment(                                  │
│       await this.stripe.charges.create({ amount, currency })   │
│     );                                                         │
│   }                                                            │
│ }                                                               │
│                                                                  │
│ class PaymentService {                                          │
│   constructor(private provider: PaymentProvider) {}             │
│                                                                  │
│   async pay(amount, currency) {                                │
│     return this.provider.createPayment(amount, currency);      │
│   }                                                            │
│ }                                                               │
│                                                                  │
│ // Easy to add new provider:                                    │
│ class PayPalProvider implements PaymentProvider { ... }         │
│ const service = new PaymentService(new PayPalProvider());       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Designing for Evolution Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION CHECKLIST                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   □ Use abstractions (interfaces, abstract classes)             │
│   □ Don't hardcode dependencies                                │
│   □ Use dependency injection                                   │
│   □ Make it easy to add new implementations                    │
│   □ Don't couple to specific libraries unnecessarily           │
│   □ Use configuration over hardcoding                          │
│   □ Design small, focused modules                              │
│   □ Make the happy path easy, but handle alternatives          │
│                                                                 │
│   When adding a feature, ask:                                  │
│   - How will this change in 6 months?                          │
│   - What new requirements might come?                          │
│   - What might need to be swapped out?                        │
│   - How can I make that swap easy?                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 4: The Pattern Library Structure

### Organization by Domain

```
PATTERN_LIBRARY/
│
├── 01-FOUNDATION/
│   ├── error-handling/
│   │   ├── try-catch-patterns.md
│   │   ├── result-patterns.md
│   │   └── error-boundaries.md
│   ├── validation/
│   │   ├── input-validation.md
│   │   └── schema-validation.md
│   └── testing/
│       ├── unit-testing.md
│       ├── integration-testing.md
│       └── e2e-testing.md
│
├── 02-DATA/
│   ├── database/
│   │   ├── crud-patterns.md
│   │   ├── migrations.md
│   │   └── query-patterns.md
│   ├── cache/
│   │   ├── cache-invalidation.md
│   │   ├── cache-strategies.md
│   │   └── distributed-cache.md
│   └── search/
│       ├── fulltext-search.md
│       └── faceted-search.md
│
├── 03-INTEGRATION/
│   ├── auth/
│   │   ├── jwt-auth.md
│   │   ├── oauth.md
│   │   ├── session-auth.md
│   │   └── api-keys.md
│   ├── payments/
│   │   ├── payment-flows.md
│   │   ├── webhook-handling.md
│   │   └── refund-patterns.md
│   ├── queues/
│   │   ├── job-queues.md
│   │   ├── scheduled-jobs.md
│   │   └── event-driven.md
│   └── notifications/
│       ├── notification-channels.md
│       ├── notification-templates.md
│       └── notification-preferences.md
│
├── 04-ARCHITECTURE/
│   ├── api-design/
│   │   ├── rest-api.md
│   │   ├── graphql.md
│   │   └── error-responses.md
│   ├── microservices/
│   │   ├── service-communication.md
│   │   ├── distributed-transactions.md
│   │   └── service-discovery.md
│   └── cqrs/
│       ├── cqrs-basics.md
│       └── event-sourcing.md
│
└── 05-OPERATIONS/
    ├── logging/
    │   ├── structured-logging.md
    │   └── log-levels.md
    ├── monitoring/
    │   ├── metrics.md
    │   └── alerting.md
    └── deployment/
        ├── ci-cd-pipelines.md
        └── containerization.md
```

---

## Part 5: How to Extract Patterns (Practical Guide)

### The Process in Action

```
Example: Let's extract the "File Upload" pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Collect 10 different file upload implementations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Implementation A: Simple upload to disk
- multer in Express
- save to /uploads
- return file path

Implementation B: S3 upload
- stream to S3
- generate presigned URL
- store metadata in DB

Implementation C: Large file upload
- chunked upload
- resume support
- progress tracking

Implementation D: Image processing upload
- upload + resize
- generate multiple sizes
- optimize format (WebP)

Implementation E: Secure upload
- virus scanning
- content type validation
- size limits

Implementation F: API with access control
- check permissions before upload
- store in user-specific folder
- rate limiting

STEP 2: Analyze each dimension
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's common:
- Receive file
- Validate file (type, size)
- Store file
- Return reference

What's different:
- Where stored (disk, S3, cloud)
- How validated (extension, magic number, virus scan)
- How processed (none, resize, compress)
- How accessed (public, private, signed URL)

STEP 3: Extract abstract pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│ FILE UPLOAD PATTERN                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌───────────┐    ┌────────────┐         │
│  │ Receive  │───▶│ Validate  │───▶│ Process    │         │
│  │ File     │    │ File      │    │ File       │         │
│  └──────────┘    └───────────┘    └─────┬──────┘         │
│                                          │                  │
│                                          ▼                  │
│  ┌──────────┐    ┌───────────┐    ┌────────────┐         │
│  │ Return   │◀───│ Store     │◀───│ Store      │         │
│  │ Response │    │ Metadata  │    │ File       │         │
│  └──────────┘    └───────────┘    └────────────┘         │
│                                                             │
│ Extensions:                                                  │
│ - Chunk upload: validate chunks, merge                     │
│ - Progress: emit progress events                           │
│ - Resume: track uploaded chunks                            │
│ - Processing: transform after upload                       │
│ - Security: virus scan, access control                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

STEP 4: Create implementation templates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each provider (disk, S3, cloudinary):
- Implement the interface
- Follow the pattern

For each variation (chunked, secure, etc.):
- Extend base implementation

STEP 5: Document when to use each
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use disk:    Small files, simple deployment, dev
Use S3:      Large files, production, need CDN
Use Cloud:   Image processing, transformations
Use chunked: Files > 100MB, unreliable networks
```

---

## Part 6: The Meta-Process

### Continuous Improvement

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATTERN IMPROVEMENT LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │ Use Pattern │ ────▶ Write code                              │
│   └──────┬──────┘                                               │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │ Encounter   │ ────▶ Hit edge case or limitation           │
│   │ Edge Case  │                                               │
│   └──────┬──────┘                                               │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │ Analyze     │ ────▶ What failed?                          │
│   │ Failure     │      Why?                                   │
│   └──────┬──────┘                                               │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │ Improve     │ ────▶ Update pattern                          │
│   │ Pattern     │      Add variation                           │
│   └──────┬──────┘      Document edge case                      │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │ Share       │ ────▶ Team learns                            │
│   │ Pattern     │                                               │
│   └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### What Makes This Different

| Traditional Approach | Pattern Approach |
|---------------------|------------------|
| Try to specify everything upfront | Learn from real code |
| Big design upfront | Iterative improvement |
| One perfect pattern | Multiple variations for context |
| Static rules | Dynamic, evolving patterns |
| Theory-based | Practice-based |

---

## Part 7: Reducing Mental Load Through Determinism

### The Problem: Cognitive Overhead

```
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE LOAD IS THE ENEMY                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   When an agent (or human) writes code, they must think about:   │
│                                                                 │
│   - What is this function supposed to do?                        │
│   - What are the edge cases?                                    │
│   - How does this handle errors?                                │
│   - What happens if X is null?                                  │
│   - What if the API call fails?                                │
│   - How does this scale?                                        │
│   - What if the database is down?                              │
│   - ...and 1000 other things                                   │
│                                                                 │
│   This is EXHAUSTING and leads to:                              │
│                                                                 │
│   - Forgotten edge cases                                        │
│   - Silent failures                                             │
│   - Incomplete error handling                                   │
│   - Bugs                                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Solution: Deterministic Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    REDUCE MENTAL LOAD THROUGH DETERMINISM            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Goal: Make the "right thing" the EASY thing                    │
│                                                                 │
│   How: Use patterns where there are fewer decisions to make     │
│                                                                 │
│   Example:                                                    │
│                                                                 │
│   BEFORE: Agent must remember to:                               │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                         │
│   - Handle loading state                                       │
│   - Handle error state                                         │
│   - Handle empty state                                         │
│   - Handle success state                                       │
│   - Implement retry logic                                      │
│   - Implement caching                                          │
│   - Invalidate cache on mutation                               │
│                                                                 │
│   AFTER: Using TanStack Query:                                 │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│   const { data, isLoading, error } = useQuery(...)            │
│                                                                 │
│   All of the above is automatically handled                     │
│   Agent just uses the data                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Applying Category Theory & Automata

#### Category Theory: Composition as the Core

```
CATEGORY THEORY PRINCIPLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━

If A → B and B → C, then we should have A → C

In code:
━━━━━━━

If:
  - fetchUser(id) → User
  - enrichUser(user) → EnrichedUser

Then we should be able to:
  - compose(fetchUser, enrichUser)(id) → EnrichedUser

┌─────────────────────────────────────────────────────────────┐
│ BENEFIT FOR AGENTS                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Instead of writing:                                         │
│                                                             │
│ async function getEnrichedUser(id) {                       │
│   const user = await fetchUser(id);                       │
│   return await enrichUser(user);                          │
│ }                                                          │
│                                                             │
│ Agent writes:                                               │
│                                                             │
│ const getEnrichedUser = compose(enrichUser, fetchUser);    │
│                                                             │
│ Less thinking, more correct                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Automata Theory: State Machines

```
AUTOMATA PRINCIPLE:
━━━━━━━━━━━━━━━━━━━━

Every system can be modeled as a finite state machine

In code:
━━━━━━━

Instead of ad-hoc state management:

  const [status, setStatus] = useState('idle');
  // Then: loading, success, error, retrying...
  // Can be: idle → loading → error → loading → success
  // Or: idle → loading → success → refreshing → success
  // Or: idle → loading → error → retrying → loading → ...

Use explicit state machine:

  type State =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: Data }
    | { status: 'error'; error: Error; retryCount: number };

  type Event =
    | { type: 'FETCH' }
    | { type: 'SUCCESS'; data: Data }
    | { type: 'ERROR'; error: Error }
    | { type: 'RETRY' };

┌─────────────────────────────────────────────────────────────┐
│ BENEFIT FOR AGENTS                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Instead of:                                                 │
│                                                             │
│ const [data, setData] = useState(null);                   │
│ const [loading, setLoading] = useState(false);            │
│ const [error, setError] = useState(null);                 │
│ // What are all the valid states?                         │
│ // What are the valid transitions?                         │
│                                                             │
│ Agent writes:                                               │
│                                                             │
│ const [state, send] = useMachine(machine);               │
│ // State is exhaustive - all cases handled                │
│ // Transitions are explicit - no invalid states           │
│ // Easier to reason about                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Practical Deterministic Patterns

#### Pattern 1: Railway-Oriented Programming

```
┌─────────────────────────────────────────────────────────────┐
│ RAILWAY-ORIENTED PROGRAMMING                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Instead of:                                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ function processUser(input) {                          │ │
│ │   const user = validate(input);                        │ │
│ │   if (!user.valid) return null;                        │ │
│ │   const saved = save(user);                           │ │
│ │   if (!saved) return null;                            │ │
│ │   const enriched = enrich(saved);                      │ │
│ │   if (!enriched) return null;                         │ │
│ │   return enriched;                                     │ │
│ │ }                                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Write:                                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ const processUser = (input) =>                         │ │
│ │   Result.of(input)                                     │ │
│ │     .map(validate)                                     │ │
│ │     .map(save)                                         │ │
│ │     .map(enrich)                                       │ │
│ │     .extract();                                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Benefits:                                                   │
│ ✓ No null checks scattered everywhere                      │
│ ✓ Explicit error handling                                  │
│ ✓ Composable                                                │
│ ✓ Agent can't forget error handling                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Pattern 2: Contract-Based Design

```
┌─────────────────────────────────────────────────────────────┐
│ CONTRACT-BASED DESIGN                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Define input/output contracts explicitly:                   │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ interface UserService {                                │ │
│ │   // PRECONDITIONS:                                    │ │
│ │   // - id must be non-empty string                     │ │
│ │   // - caller must have 'read:users' permission        │ │
│ │   getUser(id: string): Promise<User>;                 │ │
│ │                                                            │ │
│ │   // PRECONDITIONS:                                    │ │
│ │   // - user must pass validation                       │ │
│ │   // - caller must have 'write:users' permission      │ │
│ │   createUser(data: CreateUserDTO): Promise<User>;      │ │
│ │                                                            │ │
│ │   // PRECONDITIONS:                                    │ │
│ │   // - id must be non-empty string                     │ │
│ │   // - data must pass validation                       │ │
│ │   // - caller must have 'write:users' permission       │ │
│ │   updateUser(id: string, data: UpdateUserDTO):         │ │
│ │     Promise<User>;                                      │ │
│ │ }                                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Benefits:                                                   │
│ ✓ Agent knows exactly what to validate                     │
│ ✓ Agent knows exactly what permissions needed               │
│ ✓ No guessing                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Pattern 3: Effect Schema

```
┌─────────────────────────────────────────────────────────────┐
│ EFFECT SCHEMA (cf. fx.ts, io-ts)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Declare effects as data, not as implementation:             │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ const Effects = {                                       │ │
│ │   fetchUser: t.function([t.string], User),             │ │
│ │   saveUser: t.function([User], User),                 │ │
│ │   sendEmail: t.function([Email], void),               │ │
│ │ };                                                     │ │
│ │                                                         │ │
│ │ // Runtime validates:                                  │ │
│ │ // - fetchUser called with string, returns User       │ │
│ │ // - saveUser called with User, returns User          │ │
│ │ // - sendEmail called with Email, returns void        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Benefits:                                                   │
│ ✓ Agent can't call effects with wrong arguments            │
│ ✓ Effects are testable (inject mocks)                     │
│ ✓ All effects are explicit                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Summary: Reducing Mental Load

```
┌─────────────────────────────────────────────────────────────────┐
│                    HOW TO REDUCE AGENT COGNITIVE LOAD                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. USE DETERMINISTIC PATTERNS                                 │
│      - Same input → same output                                 │
│      - No hidden state                                          │
│      - Predictable behavior                                      │
│                                                                 │
│   2. USE COMPOSABLE ABSTRACTIONS                                │
│      - Category theory: compose functions                       │
│      - Chain transformations                                     │
│      - Don't write loops when you can compose                   │
│                                                                 │
│   3. USE EXPLICIT STATE MACHINES                                │
│      - All states known upfront                                 │
│      - All transitions explicit                                 │
│      - No "impossible" states                                   │
│                                                                 │
│   4. USE CONTRACTS                                              │
│      - Preconditions explicit                                   │
│      - Postconditions explicit                                  │
│      - Agent knows what to validate                             │
│                                                                 │
│   5. USE EFFECT SYSTEMS                                         │
│      - Effects declared as data                                 │
│      - Runtime validation                                       │
│      - Easier testing                                           │
│                                                                 │
│   RESULT: Agent focuses on BUSINESS LOGIC, not boilerplate     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

The pragmatic approach:

1. **Don't theorize** - Take real code and analyze it
2. **Iterate** - Keep improving patterns
3. **Extract what's common** - Abstract the patterns
4. **Handle variations** - Support different contexts
5. **Design for evolution** - Make it easy to change

This is how quality software has always been built - by learning from what works, iterating on what doesn't, and creating abstractions that capture that learning.

The key insight: **Patterns emerge from practice, not from specification.**

---

## Related Documents

- [Code Quality System](./code-quality.md) - Quality enforcement
- [Training & Verification](./train-verify.md) - Training and verification
- [Agent Knowledge System](../agent-knowledge-system.md) - Knowledge freshness

---

*Document version: 1.0*
*Last updated: 2026-03-04*
