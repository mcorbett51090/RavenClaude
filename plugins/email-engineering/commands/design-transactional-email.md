---
description: "Design a transactional email end-to-end — an idempotent send behind a provider interface, a signature-verified idempotent webhook handler, and a responsive MJML template with a plain-text part and accessibility."
argument-hint: "[the email + ESP, e.g. 'password reset via Postmark']"
---

# Design a transactional email

You are running `/email-engineering:design-transactional-email`. For the email/ESP in `$ARGUMENTS`, produce the send path, the feedback handler, and the template — the build discipline of the `email-sending-engineer` (exactly-once, renders-everywhere, learns-from-outcome).

## When to use this

You need to send a specific transactional email (receipt, password reset, alert) reliably and have it render across clients. NOT for marketing campaign strategy (→ `marketing-operations`).

## Steps

1. **Send idempotently** — derive a stable idempotency key from the business event; guard before dispatch so a retry can't double-send (`skills/transactional-email-integration/SKILL.md`).
2. **Wrap the ESP** behind a small `EmailProvider` interface (swappable, testable); add timeouts + bounded retry on 429/5xx.
3. **Handle the webhook**: verify the signature, then process idempotently and order-independently (events are at-least-once); update suppression on bounce/complaint.
4. **Build the template** in MJML (`skills/email-template-engineering/SKILL.md`) with the Outlook/Gmail/dark-mode guards, a real plain-text part, accessible markup, and links on the sending domain.
5. **Test** across clients and confirm size under the ~102KB Gmail clip threshold.

## Guardrails

- No `provider.send()` without an idempotency guard.
- No webhook processing before signature verification.
- Always ship `multipart/alternative` with a plain-text part.
- Keep the API key in the secret store, not the template repo.
