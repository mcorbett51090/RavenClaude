# Warm up new sending domains and dedicated IPs

**Status:** Strong default
**Domain:** Sending reputation
**Applies to:** `email-engineering`

---

## Why this exists

A new sending domain or dedicated IP has **no** reputation. Sending high volume on day one is exactly what a spammer who just bought a domain does, so providers throttle or junk it. Reputation is earned by a consistent ramp of **wanted** mail to **engaged** recipients — not configured. A perfectly-authenticated cold blast still lands in spam.

## How to apply

- Ramp volume over days/weeks, starting with the most engaged recipients (opens/clicks build positive signal).
- Watch Google Postmaster domain/IP reputation as you climb; slow down if it dips.
- Transactional (high-engagement, expected) warms faster than cold marketing.
- A **dedicated IP** needs sustained volume to stay warm — don't take one unless volume justifies it; otherwise a shared pool is safer.

**Do:** front-load engaged recipients; ramp gradually; monitor reputation.
**Don't:** migrate an entire list to a new domain in one send; take a dedicated IP you can't keep warm.

## Edge cases / when the rule does NOT apply

- Very low volume on a **shared** ESP IP needs little explicit warm-up (you inherit the pool reputation) — but a brand-new **domain** still benefits from a ramp.

## See also

- [`../knowledge/deliverability-fundamentals.md`](../knowledge/deliverability-fundamentals.md) — warm-up; dedicated vs shared IP.

## Provenance

ESP warm-up guidance; Google Postmaster reputation signals.

---

_Last reviewed: 2026-06-13 by `claude`_
