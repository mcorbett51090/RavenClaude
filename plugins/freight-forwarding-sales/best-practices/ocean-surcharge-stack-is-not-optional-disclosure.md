# Disclose the full ocean surcharge stack before the customer signs — no post-booking surprise charges

**Status:** Absolute rule
**Domain:** Ocean freight quoting
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

The most common source of customer complaints and disputes in ocean freight forwarding is not the base rate — it is the surcharge that appears on the invoice that was not in the quote. BAF, CAF, THC (both ends), LSS, GRI, PSS, AMS/ENS, ISPS, DDC — each charge is legitimate, but collectively they can add 30–60% to the base rate on a given lane. A customer who agreed to a base rate of USD 800/TEU and receives an invoice for USD 1,450/TEU with twelve line items they did not budget for will not re-book. A quote that names every charge — even if the total is higher than the competitor's "base-only" teaser — is a more professional, trust-building document.

## How to apply

Every ocean quote includes a full surcharge stack itemized by name and charge basis. The total at the bottom is the all-in sell price the customer can budget against.

**Minimum surcharge disclosure for ocean FCL (per TEU/container):**

```
Charge                          Basis           Amount (USD)
──────────────────────────────────────────────────────────────
Base ocean freight              Per TEU         [AMOUNT]
Bunker Adjustment Factor (BAF)  Per TEU         [AMOUNT]
Currency Adjustment Factor (CAF) Per TEU        [AMOUNT] — if applicable on this lane
Origin Terminal Handling (THC)  Per TEU         [AMOUNT]
Destination Terminal Handling   Per TEU         [AMOUNT]
Low Sulphur Surcharge (LSS)     Per TEU         [AMOUNT] — if applicable
AMS / ENS (filing fee)          Per B/L         [AMOUNT] — for US/EU filing
ISPS (security)                 Per TEU         [AMOUNT]
Documentation fee               Per B/L         [AMOUNT]
[Other lane-specific charges]   [Basis]         [AMOUNT]
──────────────────────────────────────────────────────────────
ALL-IN SELL PRICE               Per TEU         [TOTAL]
```

**Do:**
- Name every charge with its industry-standard abbreviation and full name.
- State the charge basis clearly: per TEU, per B/L, per container, per W/M.
- If a charge is marked `[EXAMPLE]` because a live rate is not yet sourced, make that explicit with a note — do not present an estimated surcharge as a confirmed figure.
- Flag any charges that are subject to change before loading (e.g., GRI/PSS announced after quote date).

**Don't:**
- Bundle surcharges into a single "additional charges" line without naming them.
- Show only the base ocean rate and add surcharges separately on the invoice — this is the exact pattern that destroys customer trust.
- Omit destination THC on an FOB or CIF quote because "the customer pays it" — you must still name it so the customer can budget it, even if it is their account.
- Use placeholder amounts from memory rather than live tariff sources; mark any estimate clearly.

## Edge cases / when the rule does NOT apply

For formal contract rates where the surcharge structure is locked in a side letter or rate card (common in annual tender outcomes), the quote may reference "surcharges as per the agreed rate card — see Annex [X]" provided that annex exists and the customer has it. The obligation to disclose does not relax; only the format changes. For road and domestic quotes where a single all-in rate is the industry norm, itemised surcharges may be collapsed — but the all-in total remains mandatory.

## See also
- [`../agents/freight-rate-quoter.md`](../agents/freight-rate-quoter.md) — all-in quote builder and surcharge stack
- [`../skills/freight-pricing-mechanics/SKILL.md`](../skills/freight-pricing-mechanics/SKILL.md) — full surcharge glossary and charge-basis guide

## Provenance

Codifies `freight-rate-quoter`'s anti-pattern check (§4 in CLAUDE.md: "A quote with a base ocean/air rate but no surcharge stack…") and house opinion §1 ("Quote all-in, never base-only"). Standard forwarding practice; reflects customer expectation norms across shipper communities globally.

---

_Last reviewed: 2026-06-05 by `claude`_
