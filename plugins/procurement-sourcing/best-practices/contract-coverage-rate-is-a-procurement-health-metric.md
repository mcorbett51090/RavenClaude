# Contract Coverage Rate Is a Procurement Health Metric

**Status:** Pattern
**Domain:** Spend analytics / contract management
**Applies to:** `procurement-sourcing`

---

## Why this exists

Spend without a contract is spend without a negotiated price, defined terms, or SLA accountability. It is also the mechanism by which realized savings evaporate: a supplier who was brought under contract at a negotiated rate reverts to their standard rate as soon as the contract lapses and orders continue on the old PO. Contract coverage rate — the percentage of addressable spend that runs through an active, in-date contract — is the leading indicator of whether the procurement function's savings and terms are being protected or eroding. A procurement function that tracks savings but not contract coverage is measuring effort without tracking whether the effort persists.

## How to apply

Include contract coverage rate in the procurement scorecard and measure it by category, supplier tier, and spend band.

```
Contract Coverage Rate — Definition and Measurement
──────────────────────────────────────────────────────
Definition:
  Contract Coverage Rate = (Spend under active contract / Total addressable spend) × 100%

"Addressable spend" excludes:
  - Spend on mandated/government-directed suppliers with no competitive option
  - Utility spend with no contract alternative (meter-rate spend)
  - Regulatory fees / taxes

Measurement cadence: Monthly for strategic and leverage categories;
                     Quarterly for bottleneck and acquisition categories.

Target tiers:
  Strategic and leverage categories:   ≥ 90%
  Bottleneck categories:               ≥ 80%
  Acquisition / one-off categories:    track but do not set a target

Segmentation:
  Report coverage by:
  - Category (Kraljic tier)
  - Supplier (top 80% of spend by supplier)
  - Business unit (to identify maverick-spend concentrations)
```

**Do:**
- Track contract expiration dates in the procurement system and build a 90-day renewal pipeline report; a contract that expires without a renewal in place becomes uncovered spend.
- Flag uncovered spend above a materiality threshold to category owners monthly; visibility is the enforcement mechanism.
- Report contract coverage rate alongside savings attainment in the procurement scorecard — they are two sides of the same coin.

**Don't:**
- Count a lapsed or expired contract as "under contract" — coverage is only real if the contract is active and the spend is ordered under its terms.
- Use "we have a master agreement" as a proxy for coverage — verify that purchase orders are referencing the agreement and that the pricing schedules are in date.
- Treat the coverage rate target as a compliance metric to be gamed; a contract with no commercial benefit created only to hit the coverage metric is not procurement value creation.

## Edge cases / when the rule does NOT apply

- **Emergency or disaster-response procurement** — post-emergency, review what was bought off-contract and decide which suppliers to bring under contract for future readiness.
- **Highly seasonal or one-off capital purchases** — contract coverage for a once-in-five-years capex purchase is less meaningful than for recurring direct materials; set the materiality threshold appropriately.

## See also

- [`../agents/spend-analytics-analyst.md`](../agents/spend-analytics-analyst.md) — owns the spend cube and the contract coverage rate metric.
- [`./realized-savings-negotiated-savings-track-to-the-pl.md`](./realized-savings-negotiated-savings-track-to-the-pl.md) — contract coverage is the mechanism that makes negotiated savings persist in the P&L; if coverage drops, savings leak.

## Provenance

Codifies the spend-analytics-analyst's contract-coverage metric discipline from the procurement-sourcing plugin's CLAUDE.md §3 #3 (realized vs negotiated savings tracking). The target-tier thresholds are standard procurement benchmark practice; mark `[unverified — training knowledge]` and validate against current benchmarks before citing to a client.

---

_Last reviewed: 2026-06-05 by `claude`_
