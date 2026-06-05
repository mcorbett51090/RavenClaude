# Occupancy Cost Is the Fixed Ceiling That Frames Every Unit Decision

**Status:** Pattern
**Domain:** Unit economics / four-wall P&L
**Applies to:** `restaurant-operations`

---

## Why this exists

Operators focus relentlessly on prime cost (food + labor) as the controllable variable and treat rent as a fixed background condition. Occupancy cost (rent + CAM + NNN fees) is not controllable in the short run, but it is the ceiling that determines whether a unit can ever be profitable at current sales. A unit paying 12% of revenue in occupancy at $1M sales is in a structurally different position than one at 8%. When occupancy exceeds 10% of revenue at full capacity, the remaining P&L has no room for error — prime cost must be held to very tight tolerances, or the unit cannot reach its return hurdle. Operators who do not explicitly model occupancy as a binding constraint misread turnaround feasibility.

## How to apply

Build the occupancy constraint test for every unit decision:

```
Occupancy cost analysis (per unit, annualized):
  Base rent:                           $______
  CAM / NNN (estimated or actual):     $______
  Other occupancy (insurance, taxes):  $______
  Total occupancy cost:                $______

  Current annual revenue:              $______
  Occupancy %:                         occupancy cost / revenue = ______%

  Occupancy benchmarks [unverified — training knowledge]:
    QSR:               target <6–8% of revenue
    Fast-casual:       target <8–10% of revenue
    Casual dining:     target <8–10% of revenue
    Fine dining:       target <10–12% of revenue (higher check average offsets)

  Breakeven sales for occupancy target:
    Breakeven sales = total occupancy / target occupancy % = $______

  If current sales < breakeven sales:
    → Unit is structurally over-rented at current volume; turnaround requires either
       (a) volume growth to target, or (b) lease renegotiation.
```

**Do:**
- Include occupancy cost explicitly in every four-wall P&L, not as a footnote.
- Model the "breakeven sales for occupancy target" before recommending any turnaround — if the volume required is not achievable, the unit may not be turnaround-viable.
- Treat lease renegotiation as a legitimate operational lever during downturns — landlords prefer a reduced-rent tenant to a vacancy.

**Don't:**
- Present a unit P&L without an occupancy cost line and occupancy-% calculation — prime cost only analysis can make a structurally over-rented unit look fixable when it isn't.
- Confuse fixed occupancy cost (rent) with fully-fixed cost (some occupancy items are semi-variable — insurance, certain utilities) — decompose accurately.

## Edge cases / when the rule does NOT apply

Ghost kitchens and virtual restaurants renting commissary time by the hour have a variable occupancy cost; the same discipline applies but the cost is not a fixed lease.

## See also

- [`../agents/restaurant-engagement-lead.md`](../agents/restaurant-engagement-lead.md) — flags occupancy constraint during the initial scoping read.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the four-wall P&L and the occupancy-% calculation.
- [`./prime-cost-is-the-master-number.md`](./prime-cost-is-the-master-number.md) — occupancy % sets the ceiling that determines how tight prime cost must be held; both must be read together.

## Provenance

Occupancy cost benchmarking and the rent-to-sales constraint are standard in restaurant lease analysis and multi-unit operator consulting; benchmarks marked `[unverified — training knowledge]` and vary by market and format.

---

_Last reviewed: 2026-06-05 by `claude`_
