# Stripe integration

> **Last reviewed:** 2026-05-21. Sources: Stripe developer docs (`stripe.com/docs`), Database Tycoon benchmark (https://www.databasetycoon.com/blog/evaluating-stripe-ingestion-frameworks-our-process-benchmarks-and-findings), Fivetran/Airbyte Stripe connector docs. Refresh when: (a) Stripe ships a new API version that affects core entities (Charges/PaymentIntents/Subscriptions), (b) an ELT vendor changes their Stripe pricing model, or (c) Stripe's webhook auth model changes.

## Auth

- **API key** (restricted keys for production)
- **Use restricted keys** — limit scope to the resources the ELT needs (read-only on Charges/Customers/Subscriptions/Invoices/Refunds/Disputes; never grant write access to an ELT pipeline)
- **Test mode vs live mode** — separate keys; never sync test data into a prod warehouse

## Rate limits

- **100 read req/sec** per account (live mode)
- **100 write req/sec** per account (live mode)
- **Higher limits available** on request through Stripe Support
- **HTTP 429 on exceed** — honor `Retry-After`, exponential backoff with ceiling

## Connector availability

| Vendor | Stripe connector | Notes |
|---|---|---|
| Fivetran | ✅ | MAR-billed; high-volume merchants will burn MAR fast on event streams |
| Airbyte | ✅ | OSS + Cloud; credit-billed in Cloud |
| Hevo | ✅ | Event-based pricing |
| Stitch | ✅ | In maintenance mode under Qlik/Talend |
| Estuary | ✅ | Real-time CDC option |

## The batch + webhook hybrid pattern

**Don't try to ELT a webhook-driven event source as if it's a CRUD database.** Stripe's value is bifurcated:

1. **Batch ELT for historical analytics** — Customers, Charges, PaymentIntents, Subscriptions, Invoices, Refunds, Disputes, Balance Transactions. Daily cadence works for most analytics.
2. **Webhooks for real-time signals** — fraud, payment success/failure, subscription state changes, dispute creation. Webhook handlers run *separately* from the ELT pipeline.

### Common pattern

```
[Stripe] --webhooks--> [Real-time event handler (Lambda / Worker)] --> [Operational alerts / dashboards]
   |
   v
[Stripe] --nightly ELT--> [Warehouse (Postgres / BigQuery / Snowflake)] --> [Analytics dashboards]
```

## Entities for analytics

| Entity | Use case | Notes |
|---|---|---|
| `customers` | Customer dimension | Email, name, metadata |
| `charges` | Successful payment fact | Legacy entity; PaymentIntents is preferred for new builds |
| `payment_intents` | Modern payment fact | Includes 3DS / SCA state |
| `subscriptions` | Recurring revenue dimension | Status, billing cycle, plan |
| `subscription_items` | Subscription line items | Multi-product subscriptions |
| `invoices` | Invoice fact | Issued, paid, voided states |
| `invoice_line_items` | Invoice line grain | For revenue recognition |
| `refunds` | Refund fact | Linked to charge or payment_intent |
| `disputes` | Dispute fact | Critical for fraud monitoring |
| `balance_transactions` | Cash-movement fact | Reconciles to bank balance |
| `payouts` | Payout fact | Stripe → bank account |
| `coupons` / `promotion_codes` | Discount dimension | For revenue analytics |

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `dim_customer` | Customer dimension (Stripe + other sources unified) |
| `dim_subscription` | Subscription dimension with status history |
| `fact_payments` | Payment-level revenue (from PaymentIntents) |
| `fact_invoice_lines` | Invoice-line grain for revenue recognition |
| `fact_refunds` | Refund fact |
| `mart_mrr` | Monthly Recurring Revenue cube |
| `mart_arr` | Annual Recurring Revenue + ARR-movement breakdown |
| `mart_churn` | Subscription churn analysis |
| `mart_payment_failures` | Failed-payment cohort + retry behavior |

## Common gotchas

1. **Charge vs PaymentIntent** — Charges is the legacy entity; PaymentIntents is the modern one. Use PaymentIntents for new analytics; both exist for older data.
2. **Subscription state transitions** — Subscription `status` changes (active → past_due → unpaid → canceled); the data warehouse should preserve the full state history, not just current
3. **Refund timing** — refunds can arrive days after the original charge; reconcile against `balance_transactions`, not `charges` alone
4. **Multi-currency** — Stripe stores `amount` in the smallest currency unit (cents for USD, yen for JPY); `currency` field is required for any aggregation
5. **Test vs live data** — keep them in separate schemas (raw_stripe_test, raw_stripe_live) to avoid analyst confusion
6. **MRR calculation requires Stripe's subscription model** — recurring vs one-time charges; one-time invoices show up as Charges/PaymentIntents but not Subscriptions
7. **Disputes don't show up immediately** — disputes can arrive 60+ days after charge; dashboards should refresh weekly minimum
8. **Webhook reliability** — webhooks can be delivered out of order or duplicated; idempotent handlers required. Use `event.id` as the dedup key.

## PII / PHI considerations

- **Customer entity has PII** — email, name, phone, billing address
- **Charge.metadata can contain PII** if the merchant put it there — audit before ELT
- **Stripe is PCI-DSS Level 1 certified** — don't store raw card numbers anywhere downstream
- **GDPR right-to-erasure** — Stripe's delete-customer API removes data from Stripe; the warehouse needs a parallel delete process

## Webhook verification

```typescript
// Stripe sends a Stripe-Signature header on every webhook
// The receiver must verify the signature before processing
import { Stripe } from "stripe";

const sig = request.headers["stripe-signature"];
let event;
try {
  event = stripe.webhooks.constructEvent(
    request.body,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  );
} catch (err) {
  return response.status(400).send(`Webhook Error: ${err.message}`);
}

// Idempotency: check event.id against a processed-events table
if (await processedEventExists(event.id)) {
  return response.status(200).send("Already processed");
}
```

## Recommended sync configuration

- **Cadence:** daily for analytics; webhooks for real-time
- **Backfill:** Stripe API supports filtering by `created` timestamp — backfill 12-24 months of history
- **Incremental cursor:** `created` for most entities; `updated_at` for Subscriptions
- **State-management:** Airbyte CDK handles cursor checkpointing; verify by stopping mid-sync and resuming

## Refresh triggers

- Stripe API version-bump (annual cadence — check Stripe Changelog)
- New Stripe product (BNPL, Identity, Issuing) becomes relevant to engagement
- Webhook event-type list changes
- ELT vendor changes pricing model for Stripe sync
- Stripe Connect (platform/marketplace use case) becomes part of the engagement — different entity set
