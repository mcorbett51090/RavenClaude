# Make sends and webhook handlers idempotent

**Status:** Absolute rule
**Domain:** Sending integration / reliability
**Applies to:** `email-engineering`

---

## Why this exists

Both halves of an email system retry: your send call retries on timeout/5xx, and the ESP delivers webhook events **at least once** (and out of order). Without idempotency, a retried send emails a customer twice, and a re-delivered `bounce` event corrupts suppression state. "Exactly-once email" is built on idempotency, not on hoping the network behaves.

## How to apply

- **Send:** derive a stable idempotency key from the business event (`order-123-receipt`), guard before dispatch (ESP idempotency header or your own "sent <key>" record). A retry is a no-op.
- **Webhook:** verify the signature, then process keyed on the event id; an already-seen event is a no-op; tolerate out-of-order (a `bounce` before `delivered`).
- Ack `2xx` only after durably recording the event (so the provider stops retrying).

**Do:** treat duplicates and reordering as the default case.
**Don't:** `provider.send()` without a guard; trust a webhook body before verifying its signature (it can poison suppression).

## Edge cases / when the rule does NOT apply

- A truly one-shot manual send may not need a persisted key — but anything triggered by an event or a queue does.

## See also

- [`../skills/transactional-email-integration/SKILL.md`](../skills/transactional-email-integration/SKILL.md) — the worked code.
- Seam: `backend-engineering` (outbox/workers), `api-engineering` (webhook contract).

## Provenance

At-least-once delivery semantics; idempotency-key patterns (mirrors `fintech-payments-engineering`'s webhook discipline).

---

_Last reviewed: 2026-06-13 by `claude`_
