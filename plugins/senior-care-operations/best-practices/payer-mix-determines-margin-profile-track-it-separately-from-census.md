# Payer Mix Determines Margin Profile — Track It Separately from Census

**Status:** Pattern
**Domain:** Senior care operations / financial management
**Applies to:** `senior-care-operations`

---

## Why this exists

Two assisted living communities with identical occupancy rates can have dramatically different margins if their payer mixes differ. A community at 92% occupancy where 60% of residents are private-pay and 40% are Medicaid waiver (AL waiver, state programs) earns a fundamentally different net revenue per occupied unit than one at 90% with 80% private-pay. Medicaid waiver rates in most states reimburse at 60–80% of private-pay market rates, and the care obligations are equivalent or higher. Tracking census without tracking payer mix allows a payer-mix deterioration to hide inside a flat occupancy number until it appears as a margin problem that looks like an expense problem.

## How to apply

Track payer mix monthly alongside census, and build the margin bridge by payer segment:

```
Payer Mix Report — [Community] [Month/Year]
───────────────────────────────────────────
              │ Census │  % of  │  Avg rate  │  Net revenue  │  Prior month │
Payer type    │ (units)│ total  │  ($/month) │  ($)          │  % of total  │
──────────────┼────────┼────────┼────────────┼───────────────┼──────────────┤
Private pay   │        │        │            │               │              │
Long-term care│        │        │            │               │              │
  insurance   │        │        │            │               │              │
AL Medicaid   │        │        │            │               │              │
  waiver      │        │        │            │               │              │
VA / veteran  │        │        │            │               │              │
Other         │        │        │            │               │              │
──────────────┼────────┼────────┼────────────┼───────────────┼──────────────┤
Total         │        │ 100%   │            │               │              │

Private-pay % target: ___% (min threshold to sustain target margin)
Current private-pay %: ___%
Trend vs. prior 3 months: [ ] Improving  [ ] Stable  [ ] Deteriorating
```

**Margin impact calculator:**

```
Payer Mix Shift Impact
──────────────────────
Private-pay rate ($/resident/month):   $___
Medicaid waiver rate ($/resident/month): $___
Rate gap:                               $___/month/unit

If private-pay mix drops by 1 percentage point on a 100-unit community at 90% occupancy:
  = 0.01 × 90 units × rate gap × 12 months = annual revenue impact: $___
```

**Do:**
- Report payer mix at every monthly operations review alongside the census and occupancy numbers — do not let it hide inside a single "average rate" figure.
- Set a minimum private-pay percentage target that your pro forma requires to hit breakeven; flag when actual mix falls below it.
- Review admissions decisions against payer type: accepting high-acuity Medicaid residents to fill vacant units improves occupancy but may worsen the margin; make that trade-off explicit before the admission.
- When state Medicaid waiver rates are updated (typically annually), reforecast the margin impact by payer-mix scenario — a rate cut that looks small per-unit is large in aggregate.

**Don't:**
- Use average rate per occupied unit as the sole pricing metric — average rate rises when Medicaid census decreases even if nothing else changes, creating a misleading "improvement" signal.
- Accept Medicaid waiver residents in a private-pay-only community without verifying the license and certification requirements — not all AL licenses permit Medicaid billing.
- Treat payer mix as a static assumption in the operating budget — communities in older buildings or lower-income submarkets experience natural private-pay erosion as residents' private funds are exhausted, and this needs to be planned for.

## Edge cases / when the rule does NOT apply

Independent living communities that are not licensed for personal care and have no Medicaid-waiver participation operate entirely on private pay; payer-mix tracking for them reduces to ensuring no Medicaid obligations are inadvertently created. Home-care agencies with purely private-pay clients have no payer-mix concern; however, those participating in both private-pay and Medicaid waiver home-care programs should apply this same framework.

## See also
- [`../agents/senior-care-finance-analyst.md`](../agents/senior-care-finance-analyst.md) — builds the acuity-based pricing model and payer-mix margin bridge.
- [`../agents/census-occupancy-strategist.md`](../agents/census-occupancy-strategist.md) — sets the admissions strategy with payer mix as a constraint.
- [`../knowledge/senior-care-economics.md`](../knowledge/senior-care-economics.md) — covers rate structure, Medicaid waiver economics, and payer mix benchmarks.

## Provenance

Codifies the payer-mix margin analysis standard in senior care operations finance; consistent with NIC (National Investment Center for Seniors Housing) reporting frameworks and senior care investment due-diligence practice [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
