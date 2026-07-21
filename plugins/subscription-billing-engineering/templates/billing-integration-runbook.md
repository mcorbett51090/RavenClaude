# Billing Integration Runbook — <product / provider>

> Staged runbook to stand up (or migrate) a recurring-billing integration. Fill each section; nothing ships until the correctness gates are green. Owned by [`billing-implementation-engineer`](../agents/billing-implementation-engineer.md); model decisions come from [`billing-systems-architect`](../agents/billing-systems-architect.md).

## 0. Context

- **Provider + pinned API version:** <e.g. Stripe Billing, API 2026-xx-xx>
- **Billing model (from architect):** <flat / tiered / per-seat / usage / hybrid>
- **Currencies / intervals:** <...>
- **Tax path:** <merchant-of-record | self-managed (Stripe Tax/Avalara/…)>
- **Environments:** <test/sandbox → prod>

## 1. Model → provider objects

- [ ] Products / prices created (immutable, versioned) matching the model
- [ ] Entitlement map defined (plan → limits/features) as a first-class model
- [ ] Trial / coupon rules encoded
- [ ] Proration rules captured in the [`proration-upgrade-test-matrix`](proration-upgrade-test-matrix.md)

## 2. Subscription lifecycle

- [ ] Checkout / hosted payment page wired (no raw card data on your servers)
- [ ] Customer portal (update payment, change plan, cancel) wired
- [ ] Local subscription model synced **from provider events**, not local writes

## 3. Webhook correctness gates (BLOCKING)

- [ ] Signature verification on the endpoint (reject unsigned/invalid)
- [ ] Event-id dedupe (processed-events store) — replays are no-ops
- [ ] Ordering by object version (stale updates ignored)
- [ ] Fast 2xx + async processing on a queue
- [ ] Dead-letter queue + alerting for poison events
- [ ] Outbound idempotency keys on all state-changing calls
- [ ] **Reconciliation job** reconverges local state to the provider on a schedule

## 4. Usage metering (if applicable)

- [ ] Meter defined (unit, granularity, rounding, window)
- [ ] Idempotent recording (stable event key) + raw-event storage
- [ ] Deterministic aggregation/rating; reported before invoice cutoff
- [ ] Counted-vs-billed reconciliation + drift alert
- [ ] Backfill/correction policy (adjust next invoice, don't mutate closed period)

## 5. Dunning

- [ ] Failure classification (hard vs soft decline)
- [ ] Retry schedule (smart/adaptive where available)
- [ ] Grace period + entitlement-downgrade rules
- [ ] Comms sequence (pre / in / recovery) with one-click card update
- [ ] Recovery-rate + involuntary-churn instrumentation

## 6. Entitlements

- [ ] Cached entitlement derived from billing state
- [ ] Explicit fail-open / fail-closed choice on unknown state
- [ ] Dunning downgrades flow through the entitlement layer

## 7. Correctness seams

- [ ] Period-attributed billing events emitted for revrec (`finance`)
- [ ] Tax calculation path confirmed (`regulatory-compliance`)

## 8. Cutover / go-live

- [ ] Test-mode end-to-end run (incl. replayed + out-of-order webhooks)
- [ ] Money-path test matrix green (upgrade/downgrade/trial/refund/dunning)
- [ ] Reconciliation dry-run vs provider shows zero drift
- [ ] Rollback plan documented

## 9. Sign-off

| Gate | Owner | Status |
|---|---|---|
| Webhook idempotency + reconciliation | billing-implementation-engineer | ☐ |
| Proration test matrix | billing-systems-architect | ☐ |
| Revrec + tax seams | finance / regulatory-compliance | ☐ |
