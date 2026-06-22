# ESP capability map — 2026

> A **dated, volatile** comparison to guide ESP selection. Feature sets, pricing tiers, and limits change often — **re-verify against the provider's current docs before quoting to a client.** Marked `[verify-at-use]` throughout.
>
> _Last reviewed: 2026-06-13 by `claude`. Confidence: Tier 2 (vendor specifics — volatile). The selection PRINCIPLES are stable; the per-vendor rows are not._

## The selection principle (stable)

Choose by the **dominant job**, then by your existing stack and cost posture:

- **Transactional-first** (receipts, resets, alerts — latency + deliverability matter most) → **Postmark, Resend, Amazon SES**.
- **Marketing / lifecycle** (lists, segments, journeys, campaign UI) → **SendGrid Marketing, Customer.io, Mailchimp, Klaviyo** (e-commerce).
- **Both** → keep them on **separate subdomains** regardless of whether one vendor or two; never blend the reputation.

## Comparison (2026-06, `[verify-at-use]`)

| Provider | Sweet spot | Webhook idempotency story | Notes |
| --- | --- | --- | --- |
| **Amazon SES** | High volume, cost-sensitive, AWS-native | SNS-delivered events; you de-dupe on `messageId` | Cheapest per-email; you own more plumbing (templates, suppression sync). Pairs with the `aws-cloud` plugin. |
| **Postmark** | Transactional, DX, speed | Signed webhooks; event IDs | Opinionated against marketing on the same account — enforces stream separation. Strong deliverability reputation. |
| **Resend** | Modern DX, React Email templates | Signed webhooks (Svix) | Developer-first; good fit alongside `frontend-engineering` React Email. |
| **SendGrid** | Blended transactional + marketing at scale | Signed Event Webhook | Broadest feature set; easy to misconfigure alignment — watch the return-path/`d=`. |
| **Mailgun** | Developer transactional + EU data residency | Signed webhooks | Good logging/analytics; EU region option. |

> Columns are illustrative of **kind**, not a benchmark. Confirm signing-secret mechanics, idempotency headers, and suppression-API shape in the current provider docs before building — these are exactly the details that drift.

## What to check for any ESP (the durable checklist)

1. **Custom domain authentication** — can you set a custom return-path and DKIM `d=` so DMARC **aligns**? (Some defaults don't align out of the box — this is the #1 setup mistake.)
2. **Idempotency** — is there a send-side idempotency key, and are webhook events signed + carrying stable IDs?
3. **Suppression API** — can you read/write the provider's suppression list to reconcile with yours and to carry it on a provider switch?
4. **Event webhooks** — delivered / bounce (hard vs soft) / complaint / open / unsubscribe, with signatures.
5. **Dedicated IP / subdomain support** — for when volume justifies isolating reputation.
6. **One-click unsubscribe** — native `List-Unsubscribe-Post` support for bulk.

## BIMI / VMC (volatile, `[verify-at-use]`)

Displaying your brand logo in the inbox via **BIMI** generally requires DMARC at `quarantine`/`reject` **and** a **VMC** (Verified Mark Certificate) or **CMC** for some mailbox providers (notably Gmail, Apple) — a paid certificate tied to a registered trademark. Requirements and which providers honor BIMI without a cert change; **verify current state before promising a client an inbox logo.**
