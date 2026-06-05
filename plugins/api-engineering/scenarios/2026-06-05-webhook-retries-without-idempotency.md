---
scenario_id: 2026-06-05-webhook-retries-without-idempotency
contributed_at: 2026-06-05
plugin: api-engineering
product: webhooks
product_version: "unknown"
scope: likely-general
tags: [webhooks, idempotency, retries, signature, at-least-once, duplicate-delivery]
confidence: high
reviewed: false
---

## Problem

A team built an outbound webhook system: on each `order.completed` event they `POST`ed a payload to the customer's registered URL, retrying on any non-2xx or timeout. Customers complained of **duplicate side effects** — orders fulfilled twice, confirmation emails sent two or three times, downstream ledgers double-credited. The producer was "working as designed" (it retried until it got a 2xx), but every retry that fired after the consumer had *already* processed the event — but failed to *respond* in time — produced a duplicate. The team had built an at-least-once delivery system and documented it as if it were exactly-once.

## Constraints context

- Webhook delivery over the public internet is **at-least-once by nature**: a slow or dropped *response* (not just a failed *delivery*) triggers a retry of a payload the consumer may have already handled. Exactly-once delivery is not achievable; exactly-once *processing* is, but only with consumer-side dedup.
- The payload had no stable event identifier — each delivery attempt looked like a fresh event to the consumer, so the consumer had no way to recognize a replay.
- There was no signature on the payload, so consumers also couldn't distinguish a legitimate retry from a spoofed request.
- The retry policy was "retry forever on non-2xx," with no backoff and no dead-letter — a permanently-failing endpoint got hammered.

## Attempts

- Tried: making the producer "only send once" by marking an event delivered after the first `POST`. Failed — the first `POST` got a 200 from the consumer *after* the producer's client had already timed out and given up waiting, so the producer marked it failed and retried; the duplicate was real. You cannot fix at-least-once on the producer alone.
- Tried: telling customers to "make their handler idempotent" with no mechanism. Unactionable — without a stable event ID in the payload, the consumer has nothing to dedup on.
- Tried (the resolution): give every event a stable ID + signature, document the at-least-once contract, and add backoff + a DLQ on the producer.

## Resolution

**Webhook delivery is at-least-once; the producer's job is to make consumer-side dedup *possible*, and to retry safely.** The fix has a producer half and a contract half:

1. **Stable event ID in every delivery.** Every event gets a unique, immutable `id` (e.g. `evt_...`) that stays the **same across all retry attempts** of that event. This is the dedup key the consumer stores — "have I already processed `evt_123`? then 200 and do nothing." A delivery-attempt counter (`X-Delivery-Attempt`) can ride alongside for observability but is *not* the dedup key.
2. **Sign the payload.** An HMAC signature header (`X-Signature: sha256=...` over the raw body + a timestamp, with the timestamp checked to bound replay) lets the consumer verify the request is genuinely from you and hasn't been tampered with or replayed by a third party. Without it, "dedup on event ID" is spoofable.
3. **Document the at-least-once contract explicitly.** The integration docs must say: "deliveries are at-least-once; you **will** occasionally receive a duplicate; dedup on `event.id`; respond 2xx only after you've durably accepted the event." The producer cannot promise exactly-once — so the contract must make the consumer's dedup responsibility unambiguous.
4. **Retry with backoff + jitter, and a dead-letter.** Replace "retry forever" with bounded exponential backoff + jitter, a max attempt count, then move the event to a dead-letter/replayable queue and surface delivery failures in the developer portal — don't hammer a down endpoint, and don't silently drop after the last retry.
5. **Treat a slow 2xx as success, not a retry trigger** where possible — but since you can't guarantee the response arrives, (1)+(3) are what actually prevent the duplicate side effect.

The mental model: the network guarantees *delivery may happen more than once*; only a stable event ID + a consumer that dedups on it guarantees *processing happens once*. The producer's contract obligation is the ID, the signature, and the honest at-least-once documentation — not an impossible exactly-once promise.

**Action for the next engineer:** if a webhook system produces duplicate side effects, don't try to make the producer send exactly once (you can't). Add a stable per-event ID that survives retries, sign the payload, document at-least-once + the dedup key loudly, and give the consumer the `event.id` to dedup on. The same shape applies to *inbound* unsafe retries — that's the `Idempotency-Key` pattern (see the idempotency skill); webhooks are its outbound mirror.

Cross-reference: complements [`../knowledge/api-design-decision-trees.md`](../knowledge/api-design-decision-trees.md) (the webhook-vs-broker push tree), [`../best-practices/build-webhook-delivery-with-retries-and-signatures.md`](../best-practices/build-webhook-delivery-with-retries-and-signatures.md), [`../best-practices/build-idempotency-keys-for-unsafe-retries.md`](../best-practices/build-idempotency-keys-for-unsafe-retries.md), and the `idempotency-key-design` skill. The `Idempotency-Key`/`RateLimit`/`Deprecation` IETF drafts are volatile — re-verify status at use `[verify-at-use]`.
