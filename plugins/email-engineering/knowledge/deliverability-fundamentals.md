# Deliverability fundamentals

> The stable mental model behind every recommendation in this plugin. Mechanics are RFC-grounded and change slowly; vendor specifics live in [`esp-capability-map-2026.md`](esp-capability-map-2026.md).
>
> _Last reviewed: 2026-06-13 by `claude`. Confidence: Tier 1 (consensus / RFC-grounded)._

## The deliverability stack (each layer gates the next)

1. **Identity & authentication** — can the receiver prove the mail is from who it claims? (SPF, DKIM, DMARC alignment.) Without this, nothing else matters.
2. **Reputation** — does this domain/IP have a track record of wanted mail? Built by consistent volume, low complaints, and engagement; destroyed by spikes, complaints, and spam-trap hits.
3. **List quality** — are you sending to people who want it and whose addresses exist? (Opt-in, hygiene, suppression.)
4. **Content & format** — does the message look legitimate? (Plain-text part, reasonable size, aligned links, no spam-trigger patterns.)
5. **Engagement** — do recipients open/reply/not-delete-unread? Mailbox providers increasingly weight this.

A failure low in the stack (auth) cannot be fixed by improving something high in the stack (content). Diagnose top-down.

## Reputation: domain vs IP

- **Shared IP** (most ESPs' default) — you inherit the pool's reputation; fine for low/medium volume, less control.
- **Dedicated IP** — you own the reputation; worth it only at sustained high volume (provider guidance often cites ~tens of thousands/week+ to keep it warm). A dedicated IP sent too little goes "cold" and hurts.
- **Domain reputation** increasingly dominates IP reputation at Gmail — which is why **subdomain stream separation** is the primary reputation lever.

## Warm-up

A new sending domain/IP has **no** reputation. Sending high volume immediately reads as a spammer who just bought a domain. Warm up by ramping volume over days/weeks, starting with your **most engaged** recipients (opens/clicks build positive signal), and watch Postmaster reputation as you climb. Transactional mail (high engagement, expected) warms faster than cold marketing blasts.

## Where you read reputation (the monitoring surfaces)

Reputation is provider-specific, so you watch it on each major provider's own surface — not one dashboard:

- **Google Postmaster Tools** — domain/IP reputation, spam rate, authentication pass rates, and encryption, **for Gmail**.
- **Microsoft SNDS** (Smart Network Data Services) + **JMRP** (Junk Mail Reporting Program) — IP volume, complaint, and spam-trap data, plus the Outlook/Hotmail feedback loop, **for the Microsoft mailboxes** (Outlook.com / Hotmail / Live).
- **DMARC RUA aggregate reports** — provider-agnostic: who is sending as you, and whether each stream aligns.

A diagnosis that only checks Postmaster is **blind to Outlook/Hotmail** — register SNDS/JMRP too, because Microsoft reputation moves independently of Gmail's. These are leading indicators; read them *before* the bounce report, not after.

## The two rates that matter most

- **Hard bounce rate** — invalid/nonexistent addresses. High bounce = poor list hygiene = a spam signal. Suppress hard bounces permanently.
- **Spam-complaint rate (FBL)** — recipients hitting "report spam." The single strongest negative signal. Keep it far below ~0.3% (Gmail's stated concern level — verify current). One complaint is worth many "no opens."

## Stream separation (the architecture rule)

Send **transactional** (receipts, password resets, alerts — expected, high-engagement) and **marketing** (newsletters, promos — lower engagement, complaint-prone) from **separate subdomains**:

- `notifications.example.com` (or `mail.`) → transactional
- `news.example.com` (or `marketing.`) → marketing

So a marketing reputation dip — inevitable over time — can never delay a password-reset email. Each subdomain authenticates independently and accrues its own reputation.

## One-click unsubscribe (RFC 8058)

For bulk mail, provide both headers so the mailbox client renders a native unsubscribe button and POSTs the opt-out without the user leaving their inbox:

```
List-Unsubscribe: <https://example.com/unsub?u=...>, <mailto:unsub@example.com>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

Honor it fast. A working unsubscribe **prevents** complaints, which are far more damaging than an unsubscribe. Treat unsubscribe as a deliverability feature, not a compliance chore.

## Spam traps & list buying

Never buy or scrape lists. Purchased lists contain **spam traps** (addresses that exist only to catch senders who didn't get consent) and dead addresses; hitting them is a fast path to a blocklist. Confirmed opt-in (and re-confirmation of stale subscribers) is the only safe acquisition.
