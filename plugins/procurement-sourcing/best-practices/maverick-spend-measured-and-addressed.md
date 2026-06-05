# Measure Maverick Spend and Address Its Root Cause

**Status:** Pattern
**Domain:** Spend analytics / compliance
**Applies to:** `procurement-sourcing`

---

## Why this exists

Maverick spend — purchases made outside of approved procurement channels, preferred suppliers, or negotiated contracts — is the single biggest driver of realized-savings leakage. Negotiated rates are only realized if purchases flow through the contract; every purchase made off-contract at a non-preferred supplier resets the unit economics to the market rate (or worse). Most procurement functions underestimate maverick spend because the spend cube only shows what was bought, not whether it was bought compliantly. A function that doesn't measure maverick spend cannot know whether its savings program is working.

## How to apply

Measure maverick spend as a defined metric in the spend analytics process.

```
Maverick Spend Measurement
──────────────────────────────────────────────────────
Definition:
  Maverick spend = spend on categories or suppliers where a preferred
  contract or approved supplier list exists, but the purchase was not
  made through that contract or supplier.
  (Excludes: spend in categories with no preferred contract;
   single-source categories; emergency purchases with documented justification.)

Measurement approach:
  Step 1 — Build the "should be contracted" list:
    Categories with active preferred contracts × estimated demand volume.
  Step 2 — Match actual PO data to preferred-contract suppliers:
    PO supplier matches preferred list → compliant spend.
    PO supplier does not match → maverick spend.
  Step 3 — Calculate:
    Maverick Spend Rate = (Maverick spend $) / (Addressable spend in contracted categories $) × 100%
  Step 4 — Segment by root cause:
    a) Stakeholder didn't know about the contract / preferred supplier
    b) Stakeholder knew but found the process inconvenient (catalog / PO lead time)
    c) Stakeholder deliberately bypassed for a relationship or preference
    d) Contract is not fit for purpose (wrong product range, wrong terms)

Action by root cause:
  a) → Communication and awareness; update catalog or intranet
  b) → Remove the friction (streamline ordering; check catalog completeness)
  c) → Management escalation and policy enforcement
  d) → Category strategy refresh; contract amendment
```

**Do:**
- Include maverick spend rate in the monthly procurement scorecard alongside savings attainment.
- Investigate root cause before prescribing a fix — most maverick spend is root cause (a) or (b); enforcement should be the last resort.
- Set a target maverick spend rate and track progress against it; industry benchmark is typically < 10–15% of addressable spend.

**Don't:**
- Report only total maverick spend in dollars without the rate — a growing business with a stable dollar amount of maverick spend may actually be improving as a percentage.
- Treat all maverick spend as misconduct; most is friction-driven and amenable to process improvement.
- Measure maverick spend once and declare the category clean; it regenerates as staff turn over and processes drift.

## Edge cases / when the rule does NOT apply

- **Decentralized organizations** where business units have legitimate delegated authority to source independently in certain categories — define the boundary between central contract compliance and delegated authority explicitly; maverick spend is measured within the central-contract perimeter only.

## See also

- [`../agents/spend-analytics-analyst.md`](../agents/spend-analytics-analyst.md) — owns the spend analytics including maverick spend measurement.
- [`./contract-coverage-rate-is-a-procurement-health-metric.md`](./contract-coverage-rate-is-a-procurement-health-metric.md) — contract coverage is the precondition for measuring maverick spend; you cannot identify off-contract purchases without knowing which spend should be on contract.

## Provenance

Codifies the spend-analytics-analyst's savings-leakage discipline from the procurement-sourcing plugin's CLAUDE.md §3 #3 (realized savings ≠ negotiated savings) and §3 #5 (spend visibility comes before strategy). The 10–15% industry benchmark is from standard procurement research; mark `[unverified — training knowledge]` and validate before citing to a client.

---

_Last reviewed: 2026-06-05 by `claude`_
