# Transactional email spec — <email name>

> One-page spec for a single transactional email. Fill the brackets before building.

## Purpose & trigger

- **Email:** `<e.g. password reset>`
- **Triggered by:** `<business event, e.g. user requests reset>`
- **Stream / subdomain:** `<transactional subdomain, e.g. notifications.example.com>`
- **Idempotency key:** `<stable key derived from the event, e.g. reset-{userId}-{requestId}>`

## Send path

- **Provider:** `<ESP>` (behind the `EmailProvider` interface)
- **Idempotency guard:** ☐ checked before dispatch (no double-send on retry)
- **Timeout / retry:** `<timeout>`, retry on 429/5xx with backoff+jitter, no retry on 4xx
- **Headers:** `From`, `Reply-To`, `List-Unsubscribe` (if applicable)

## Content

- **Subject:** `<subject>`
- **Preheader:** `<preheader text>`
- **Primary action:** `<CTA + URL on the sending domain>`
- **Plain-text part:** ☐ present (multipart/alternative)
- **Personalization:** `<fields>`

## Template (rendering)

- **Authoring:** MJML ☐ / raw table HTML ☐
- **Client guards:** Outlook (Word engine) ☐ · Gmail clip <102KB ☐ · dark mode ☐
- **Accessibility:** `lang` ☐ · `role="presentation"` tables ☐ · image `alt` ☐ · contrast ☐

## Feedback loop

- **Webhook events handled:** delivered ☐ · hard bounce ☐ · soft bounce ☐ · complaint ☐
- **Signature verified before processing:** ☐
- **Handler idempotent (event-id keyed):** ☐
- **Suppression updated on hard bounce / complaint:** ☐

## Test plan

- [ ] Cross-client render (matrix / Litmus / Email on Acid)
- [ ] Dark-mode pass
- [ ] Idempotency: double-trigger sends exactly one email
- [ ] Webhook: duplicate + out-of-order events leave state correct
