# Deliver webhooks with retries, signatures, and a replay endpoint

**Status:** Pattern
**Domain:** API build craft / webhooks
**Applies to:** `api-engineering`

---

## Why this exists

Webhooks are an API contract where your server is the caller and the consumer's server is the target. Unlike a request/response API, you have no control over whether the consumer is up when you fire. A webhook without retries is a fire-and-forget notification that silently fails when the consumer is down. Without an HMAC signature, any party who learns the endpoint URL can forge events. Without a replay endpoint, a consumer who was down for a weekend has no way to recover missed events without re-importing from scratch.

## How to apply

```typescript
// 1. Sign the payload
function sendWebhook(url: string, payload: object, secret: string) {
  const body = JSON.stringify(payload);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = crypto
    .createHmac('sha256', secret)
    .update(`${timestamp}.${body}`)
    .digest('hex');

  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Webhook-Timestamp': timestamp,
      'X-Webhook-Signature': `sha256=${signature}`,
    },
    body,
  });
}

// 2. Retry with exponential backoff — idempotent: include event ID in payload
// Retry on 5xx, timeout, or network error; stop on 4xx (likely misconfigured endpoint)
const schedule = [0, 30, 120, 600, 3600]; // seconds

// 3. Replay endpoint — consumer fetches missed events by time window
// GET /webhooks/events?after=<ISO-datetime>&type=order.placed
```

**Do:**
- Include a unique `eventId` in every webhook payload — consumers use it for deduplication.
- Include the `X-Webhook-Timestamp` in the HMAC to prevent replay attacks (reject events older than 5 minutes).
- Expose a `/webhooks/events` replay endpoint so consumers can recover missed events by time window.
- Retry on `5xx` / timeout with exponential backoff; do **not** retry on `4xx` (the consumer rejected it).

**Don't:**
- Send webhooks without a signature — unsigned webhooks are unauthenticated POST requests to any endpoint.
- Retry indefinitely without a final DLQ or admin alert for permanently failed deliveries.
- Include the full secret in the webhook URL or as a query parameter.

## Edge cases / when the rule does NOT apply

Internal webhook-style calls within the same private network between services you own may omit the HMAC in favor of mutual TLS. A webhook that carries only a notification ID (and the consumer must re-fetch the full resource) simplifies replay but still needs retries and a signature.

## See also

- [`../agents/api-implementation-engineer.md`](../agents/api-implementation-engineer.md) — owns webhook build craft and retry semantics.
- [`./build-idempotency-keys-for-unsafe-retries.md`](./build-idempotency-keys-for-unsafe-retries.md) — the `eventId` in webhooks serves the same deduplication role as an `Idempotency-Key`.

## Provenance

Stripe, GitHub, and Svix webhook delivery patterns. Standard webhook reliability and security practice. Codifies `api-implementation-engineer`'s webhook responsibilities.

---

_Last reviewed: 2026-06-05 by `claude`_
