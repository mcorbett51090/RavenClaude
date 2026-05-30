# Webhooks for events, batch for history — don't ELT an event stream as if it were a table

**Status:** Pattern — strong default for event-shaped sources (Stripe, Shopify, webhook-capable SaaS); deviate only when the source has no webhook surface or real-time signals aren't part of the deliverable.

**Domain:** Connector design / source-shape modeling

**Applies to:** `data-platform`

---

## Why this exists

Event-shaped sources (Stripe charges/refunds, Shopify orders/inventory, anything with a webhook surface) have *two* faces, and forcing them into one pipeline shape breaks one of them. Treating the source as a CRUD table — nightly full/incremental batch only — means real-time signals (a payment succeeded, inventory hit zero) arrive up to a day late, useless for any operational dashboard. Treating it as webhooks-only means you have no reliable way to load **history** (webhooks only fire going forward) and a missed/duplicated delivery silently drops or double-counts. The correct shape is a **hybrid**: a batch ELT pull for the historical backfill and ongoing reconciliation, plus webhooks for low-latency event capture — landed raw, deduped on event ID, and reconciled in dbt so the two sources agree. The batch run is also the safety net that heals missed webhooks. Webhooks are an at-least-once delivery channel, not a database.

## How to apply

Run batch for backfill + reconciliation; subscribe webhooks for real-time; dedupe on event ID and reconcile the two in dbt.

```yaml
# Two ingestion paths into the SAME raw landing, reconciled downstream.
batch:        # history + nightly reconciliation safety net
  source: stripe
  mode: incremental            # backfill all charges, then catch anything webhooks missed
  cursor: created
webhooks:     # real-time signals
  events: [charge.succeeded, charge.refunded]
  delivery: at-least-once      # → MUST dedupe on event id; treat as replayable
  sink: stripe_raw.events
```

```sql
-- dbt: dedupe at-least-once webhook events on their event id; reconcile vs batch in a test.
select * from (
  select *, row_number() over (partition by event_id order by received_at desc) as rn
  from {{ source('stripe_raw', 'events') }}
) where rn = 1     -- last delivery wins; duplicate deliveries collapse
```

**Do:**
- Use **batch** for historical backfill and as the nightly reconciliation/heal path for missed webhooks.
- Use **webhooks** for low-latency operational signals; land them raw and dedupe on the event ID (at-least-once delivery).
- Reconcile the two paths in dbt (a singular test asserting webhook-derived totals tie to the batch source).
- Verify webhook signatures and treat the endpoint as a replay-safe, idempotent sink.

**Don't:**
- ELT a webhook-driven event source as if it were a CRUD table (loses real-time, or loses history).
- Rely on webhooks alone for completeness — a missed delivery is silent data loss without the batch heal.
- Append webhook events without event-ID dedup (a redelivery double-counts).

## Edge cases / when the rule does NOT apply

- **No webhook surface** (legacy/limited APIs) — batch incremental is the only path; document the freshness ceiling that imposes.
- **Real-time not in scope** — if the dashboard is daily and no operational signal is needed, batch-only is simpler and correct; don't add a webhook listener nobody consumes.
- **CDC-capable sources** — log-based replication (Fivetran HVR / Debezium) gives near-real-time without a separate webhook path; the hybrid collapses into the CDC stream.

## See also

- [`./ingest-idempotent-and-replayable.md`](./ingest-idempotent-and-replayable.md) — the event-ID dedup that makes the webhook sink replay-safe
- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — the batch backfill path of the hybrid
- [`./dashboard-set-data-freshness-slas.md`](./dashboard-set-data-freshness-slas.md) — webhooks vs batch sets the achievable freshness SLA
- [`../knowledge/stripe-integration.md`](../knowledge/stripe-integration.md) / [`../knowledge/shopify-integration.md`](../knowledge/shopify-integration.md) — per-source webhook+batch specifics
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) — owns the hybrid design

## Provenance

Distilled from `etl-pipeline-engineer.md` ("Webhooks for events; batch for history. Don't try to ELT a webhook-driven event source as if it's a CRUD database") + CLAUDE.md anti-pattern "Stripe ingestion via batch-only without considering webhooks," and the Stripe/Shopify knowledge briefs (batch ELT for history + webhooks for real-time hybrid). `[verify-at-build]` Stripe event names (`charge.succeeded`) and Shopify webhook topics — confirm against current Stripe/Shopify API docs; event taxonomies version over time.

---

_Last reviewed: 2026-05-30 by `claude`_
