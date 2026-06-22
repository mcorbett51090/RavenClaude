---
name: transactional-email-integration
description: Integrate an Email Service Provider (SES, SendGrid, Postmark, Resend, Mailgun) for transactional sending with idempotent sends, signature-verified and idempotent webhook event handling (delivered/bounce/complaint/open), and retry/rate-limit discipline. Reach for this when the user says "wire up <ESP>", "send receipts/password resets", or "handle delivery webhooks". Used by `email-sending-engineer` (primary).
---

# Skill: transactional-email-integration

> **Invoked by:** `email-sending-engineer` (primary).
>
> **When to invoke:** "integrate <ESP>"; "send a transactional email"; "handle the bounce/complaint webhook"; "our sends double under retry".
>
> **Output:** a send path with idempotency + a verified, idempotent webhook handler that closes the feedback loop into suppression.

## Procedure

1. **Pick the ESP by the seam, not the logo.** Transactional-first (Postmark, Resend, SES) vs marketing/blended (SendGrid, Mailgun). Map against [`../../knowledge/esp-capability-map-2026.md`](../../knowledge/esp-capability-map-2026.md). Wrap whichever you pick behind a small `EmailProvider` interface so it's swappable and testable.
2. **Make the send idempotent.** Derive a stable idempotency key from the business event (`order-123-receipt`), not a UUID generated at call time. Use the ESP's idempotency header where it exists; otherwise record "sent <key>" in your store and check before sending. A retried call must **not** produce a second email.
3. **Send with timeouts + bounded retries.** Treat the ESP call like any external dependency: short timeout, retry on 429/5xx with exponential backoff + jitter, and a dead-letter path. Do **not** retry a 4xx validation error.
4. **Verify the webhook, then process.** Verify the provider's signature (SES SNS signature, SendGrid/Postmark signing secret) **before** trusting the payload — an unverified webhook endpoint is an open suppression-injection hole.
5. **Make the handler idempotent and order-independent.** Providers deliver events **at least once** and out of order. Key on the event id; an already-seen event is a no-op. A `bounce` arriving before `delivered`, or twice, must not corrupt state.
6. **Close the loop into suppression.** A `bounce` (hard) or `complaint` event updates the suppression list ([`../bounce-complaint-suppression/SKILL.md`](../bounce-complaint-suppression/SKILL.md)) that the next send checks. This is the whole reason to handle webhooks.

## Worked example (language-agnostic; Node shown)

```js
// send — idempotent on a business key, behind a provider interface
async function sendReceipt(orderId, to) {
  const key = `order-${orderId}-receipt`;
  if (await sends.has(key)) return; // already sent — idempotent
  await provider.send({
    to,
    template: "receipt",
    idempotencyKey: key, // provider-side guard where supported
    headers: { "List-Unsubscribe": "<mailto:unsub@example.com>" },
  });
  await sends.put(key);
}

// webhook — verify, then idempotent process
function handleEvent(req) {
  if (!provider.verifySignature(req)) return res.status(401);
  for (const e of provider.parse(req.body)) {
    if (events.seen(e.id)) continue; // at-least-once delivery — dedupe
    events.mark(e.id);
    if (e.type === "bounce" && e.hard) suppression.add(e.email, "hard_bounce");
    if (e.type === "complaint") suppression.add(e.email, "complaint");
  }
  return res.status(200); // ack so the provider stops retrying
}
```

## Guardrails

- Never `await provider.send()` without an idempotency guard — retries and double-submits will double-send.
- Never trust a webhook body before verifying its signature; that endpoint can poison your suppression list.
- Return `2xx` only after you've durably recorded the event — a `200` tells the provider to stop retrying.
- Keep the API key in the secret store, never in the template repo (the hook flags a leaked key).
