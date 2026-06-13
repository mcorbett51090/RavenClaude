# Volatile deliverability claims carry retrieval dates

**Status:** Absolute rule
**Domain:** Accuracy discipline
**Applies to:** `email-engineering`

---

## Why this exists

The mechanics (SPF/DKIM/DMARC RFCs) are stable, but the **specifics** drift constantly: Gmail/Yahoo bulk-sender thresholds and effective dates, the exact spam-rate concern level, BIMI/VMC certificate requirements and which providers honor them, ESP feature sets and limits. Quoting a stale threshold to a client as current fact is the confident-reasoning error the marketplace accuracy discipline exists to prevent — and here it can cause a real compliance miss.

## How to apply

- Tag every volatile claim with a retrieval date and a `[verify-at-use]` rider (the knowledge bank and ESP map already do).
- Re-verify the current Gmail/Yahoo postmaster guidance and the ESP's docs **before** a client commitment or a published threshold.
- Separate the **stable principle** (authenticate, align, one-click unsubscribe, low complaints) from the **volatile number** (the exact %, the exact volume bar).

**Do:** cite the date; re-fetch before quoting; mark training-recalled specifics `[unverified — training knowledge]`.
**Don't:** state a 2024-era threshold as today's requirement without re-checking.

## Edge cases / when the rule does NOT apply

- RFC-level mechanics (how DMARC alignment works) don't need a fresh date each time — they're Tier-1 stable. The rider is for vendor/provider specifics.

## See also

- [`../knowledge/esp-capability-map-2026.md`](../knowledge/esp-capability-map-2026.md) — dated, `[verify-at-use]` throughout.
- Root accuracy discipline: [`../../../AGENTS.md`](../../../AGENTS.md) § "Accuracy discipline".

## Provenance

Marketplace accuracy discipline (AGENTS.md); the volatility of mailbox-provider sender rules.

---

_Last reviewed: 2026-06-13 by `claude`_
