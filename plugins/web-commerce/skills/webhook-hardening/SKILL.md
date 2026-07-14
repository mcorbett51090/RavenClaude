---
name: webhook-hardening
description: "Harden a commerce webhook handler: verify the provider signature with a constant-time compare BEFORE parsing the body, then de-duplicate retried deliveries by provider event id. Use when writing or reviewing any Stripe/Square/Shopify webhook receiver. Two invariants (verify-before-parse, event-id idempotency) that are non-negotiable."
---

# Webhook Hardening

Two non-negotiable invariants for every webhook handler this plugin scaffolds. Both are enforced by the [`commerce-gold-standard-rubric`](../commerce-gold-standard-rubric/SKILL.md) (dimensions 2 and 3).

## Invariant 1 — verify (constant-time) BEFORE parsing

1. Read the **raw** body — do not parse or re-serialize it first (that changes bytes and invalidates the signature).
2. Recompute the signature and compare with `safeSignatureEqual` from `templates/shared/webhook-verify.ts` — a constant-time compare. A plain `===` leaks timing an attacker uses to forge signatures.
3. On mismatch, drop the request (4xx). Only a verified request proceeds.

Per-provider scheme:

| Provider | Header | Signed over | Notes |
|---|---|---|---|
| **Stripe** | `Stripe-Signature` | payload + `whsec_` secret | 5-min timestamp tolerance guards replays |
| **Square** | `x-square-hmacsha256-signature` | signatureKey + notificationUrl + rawBody | HMAC-SHA256 |
| **Shopify** | `X-Shopify-Hmac-Sha256` | rawBody | base64 HMAC-SHA256 |

## Invariant 2 — idempotency (exactly-once)

Providers **retry** deliveries and do **not** guarantee ordering. Before any side effect:

1. Extract the provider event id (Stripe `event.id`, Square `event_id`, Shopify delivery id).
2. `await store.seen(eventId)` — if true, return 2xx and stop (already processed).
3. Do the work, then `await store.remember(eventId, ttl)`.

Use an `IdempotencyStore` (`templates/shared/idempotency-store.ts`). **On a static tier the store is KV-backed** (Upstash / Vercel KV) behind a serverless function — never a process-memory `Set` (a recycled invocation loses it and re-processes) and never browser state.

## Also

- Return **2xx fast**, then process heavy work async — providers time out and retry on a slow 2xx.
- Store only safe fields (card type / last4 / expiry), never the PAN.
- Mutating API calls carry their own idempotency key (separate from webhook dedup) — see [`payment-lifecycle-contract`](../payment-lifecycle-contract/SKILL.md).
