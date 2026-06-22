# Separate transactional and marketing mail by subdomain

**Status:** Strong default
**Domain:** Sending architecture / reputation
**Applies to:** `email-engineering`

---

## Why this exists

Marketing mail is complaint-prone and lower-engagement; its sending reputation will dip over time. Transactional mail (receipts, password resets, alerts) is expected and high-engagement, and it is **business-critical** — a password-reset email landing in spam is an outage. If both share a sending domain/subdomain, a marketing reputation dip drags transactional mail down with it. Domain reputation increasingly dominates IP reputation at Gmail, so the subdomain is the primary isolation lever.

## How to apply

- Send transactional from one subdomain (`notifications.example.com` / `mail.`) and marketing from another (`news.example.com` / `marketing.`).
- Authenticate each subdomain independently; each accrues its own reputation.
- Scope suppression by stream — a marketing unsubscribe must not suppress transactional mail.

**Do:** split the streams before volume grows; keep transactional pristine.
**Don't:** send newsletters and receipts from the same `From:` subdomain.

## Edge cases / when the rule does NOT apply

- Very low total volume from a tiny sender may not justify two subdomains yet — but design the `From:` so splitting later is a config change, not a migration.
- Some ESPs (e.g. Postmark) enforce the split at the account level — lean into it.

## See also

- [`../knowledge/deliverability-fundamentals.md`](../knowledge/deliverability-fundamentals.md) — reputation: domain vs IP; stream separation.

## Provenance

Mailbox-provider reputation guidance; ESP stream-separation conventions.

---

_Last reviewed: 2026-06-13 by `claude`_
