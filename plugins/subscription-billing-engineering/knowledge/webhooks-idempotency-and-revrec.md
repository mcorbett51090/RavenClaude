# Knowledge: Webhooks, Idempotency, Reconciliation & Revenue Recognition

> **Last reviewed:** 2026-07-21 · **Confidence:** high for the correctness patterns (provider-agnostic, stable); ASC 606 mechanics summarized at a literacy level — `finance` owns the accounting; jurisdictional tax owned by `regulatory-compliance`.
> Source of truth for [`implement-metered-billing`](../skills/implement-metered-billing/SKILL.md) and the correctness discipline of both agents. Re-read on demand.

The billing provider is the **source of truth**; your database is a cache that must reconverge to it. Webhooks are **at-least-once**, can arrive **out of order**, and can be **replayed**. Design for that from day one.

## Webhook correctness checklist

1. **Verify the signature first.** Reject events without a valid provider signature — treat the endpoint as an untrusted inbound request. Never act on an unsigned payload.
2. **Dedupe by event id (idempotency).** Persist processed event ids; a re-delivered event id is a no-op. This is what makes at-least-once delivery safe.
3. **Order by object version, not arrival.** A `subscription.updated` can arrive before the `created` it supersedes. Apply state by the object's version/updated-at, ignoring stale updates — don't trust arrival order.
4. **Return 2xx fast; process async.** Acknowledge quickly and do the work on a queue, so a slow handler doesn't cause the provider to retry (and duplicate) unnecessarily.
5. **Dead-letter poison events.** An event that repeatedly fails goes to a DLQ with alerting — never an infinite retry loop that blocks the stream.
6. **Reconcile on a schedule.** A job periodically fetches provider state and reconverges local subscription/entitlement/usage state. This is the safety net for any webhook that was missed, dropped, or applied out of order. It is **not optional**.

## Idempotency on outbound calls

Send an **idempotency key** on every state-changing provider call (create subscription, charge, refund). A network timeout must be safely retryable without creating a duplicate. Derive the key from the business operation (e.g. `checkout:{cart_id}`), not a random per-attempt value.

## Idempotency for usage metering

Usage events dedupe by a **stable caller-supplied event key**; store raw events so aggregation is replayable and reconciliation can compare counted-vs-billed. See [`implement-metered-billing`](../skills/implement-metered-billing/SKILL.md).

## Revenue recognition (ASC 606) — literacy, not accounting authority

Billed ≠ recognized. Under **ASC 606 / IFRS 15**, revenue is recognized as the performance obligation is satisfied — for a subscription, typically **ratably over the service period**, not at invoice. Practical consequences for the billing system:

- **Annual paid upfront** → cash now, but recognized 1/12 per month; the difference is **deferred revenue**.
- **Usage/overage** → recognized in the period the usage occurs.
- **Mid-cycle proration, refunds, credits** → adjust the recognition schedule, not just cash.

The billing system's job is to **produce clean, auditable billing events** (amounts, periods, proration, credits) that `finance` turns into recognition schedules. A model that can't emit period-attributed billing events can't support revrec — flag that seam early.

## Sales tax / VAT / GST

Tax is calculated at invoice time based on the customer's jurisdiction and product taxability, and the rules are **volatile and jurisdictional** — owned by `regulatory-compliance`. Two implementation paths:

- **Merchant-of-record** (e.g. Paddle) absorbs tax liability and calculation — less work, less control, lower margin.
- **Self-managed** (Stripe Tax / Avalara / TaxJar) — you keep control and margin but own registration, calculation, filing seams.

Decide the path deliberately; it changes the billing architecture.

## The failure modes this prevents

| Skipped safeguard | Failure |
|---|---|
| No signature verification | Forged events change billing state |
| No event-id dedupe | Re-delivered webhook double-provisions / double-charges |
| Trusting arrival order | Stale update overwrites current subscription state |
| No reconciliation job | A single missed webhook leaves a customer wrongly entitled/unentitled forever |
| No outbound idempotency key | A timeout-retry creates a duplicate subscription or charge |
| No period-attributed billing events | Revenue recognition can't be produced or audited |
