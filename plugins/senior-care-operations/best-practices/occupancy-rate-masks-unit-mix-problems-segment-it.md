# Occupancy Rate Masks Unit-Mix Problems — Segment It

**Status:** Pattern
**Domain:** Census analytics / capacity management
**Applies to:** `senior-care-operations`

---

## Why this exists

An aggregate occupancy rate — total occupied units ÷ total licensed units — hides the unit-mix story. A community reporting 89% overall occupancy may be at 100% occupancy for studio apartments and 72% for two-bedroom units, or at 100% for standard AL and 65% for memory care. Each of those scenarios has a different operational and financial implication. Studio waitlists with two-bedroom vacancies suggest a product-mix or pricing problem. Memory care vacancies with full AL suggest a demand signal, a clinical reputation concern, or a competitive positioning issue specific to memory care. Acting on a single aggregate number without the segmented view leads to the wrong interventions.

## How to apply

Report occupancy at the unit-type and service-level segment, not only in aggregate.

```
Occupancy segmentation report (monthly):
Minimum segments:
  - By care level: Independent Living / Assisted Living / Memory Care
  - By unit type: studio, 1-bedroom, 2-bedroom, companion suite
  - Combination view: care level × unit type (e.g., Memory Care studios vs. AL 1-bedrooms)

For each segment:
  - Units occupied / licensed units
  - Occupancy %
  - Waitlist length (if any)
  - Average rent per unit for the segment
  - Revenue per occupied unit (RPO)
  - Trend: current month vs. 3-month average vs. prior year same month

Diagnostic flags:
  - Any segment below 80% occupancy: investigate sales, pricing, and competitive positioning
    for that specific segment
  - Any segment at 100% with a waitlist: evaluate pricing opportunity (rate is below demand)
  - Significant revenue per occupied unit variance between segments: flag for acuity and
    rate analysis

Unit-mix strategy review (quarterly):
  - Is the unit-mix aligned with market demand in the catchment area?
  - Is a high-vacancy unit type underpriced, overpriced, or simply mispositioned in the market?
  - Can any low-demand unit type be repositioned (e.g., AL studio converted to memory care)?
```

**Do:**
- Present segmented occupancy data in the same report as the aggregate — the aggregate as the headline, the segments as the diagnosis.
- Assign a sales strategy (specific outreach, pricing review, or referral channel focus) to each segment below 80%, not to the aggregate.
- Review unit-mix alignment with market demand annually — the catchment area's demographic and competitor landscape changes.

**Don't:**
- Celebrate 90% aggregate occupancy without confirming no segment is below 80% — a memory care wing at 65% is a strategic and financial problem even if overall occupancy looks healthy.
- Apply a uniform discount or rate incentive across all units to fill vacancies — a targeted incentive for the specific vacant unit type is more margin-protective and more effective.
- Treat a waitlist for one unit type as a sign of overall community health without investigating whether the popular units are underpriced.

## Edge cases / when the rule does NOT apply

Very small communities (under 20 units) with only one or two unit types have limited statistical meaning in segment-level occupancy — the aggregate and a simple unit-type breakdown are sufficient; the principle still applies conceptually.

## See also

- [`../agents/census-occupancy-strategist.md`](../agents/census-occupancy-strategist.md) — owns census analytics and occupancy strategy.
- [`../agents/senior-care-finance-analyst.md`](../agents/senior-care-finance-analyst.md) — revenue per occupied unit and unit-mix financial analysis belong in the practice scorecard.
- [`./census-is-the-revenue-engine-manage-the-flow-not-just-the-nu.md`](./census-is-the-revenue-engine-manage-the-flow-not-just-the-nu.md) — the flow principle applies at the segment level, not only in aggregate.

## Provenance

Standard senior care and senior housing operations analytics; codifies best practice in occupancy reporting as applied in NIC MAP analytics and senior housing consulting frameworks; the aggregate-vs-segment distinction is a fundamental operations management principle applied to the senior care context.

---

_Last reviewed: 2026-06-05 by `claude`_
