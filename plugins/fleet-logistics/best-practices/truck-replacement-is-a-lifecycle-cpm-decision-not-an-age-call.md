# Truck Replacement Is a Lifecycle CPM Decision, Not an Age Call

**Status:** Pattern
**Domain:** Fleet maintenance / asset lifecycle
**Applies to:** `fleet-logistics`

---

## Why this exists

Replacing a truck "because it's old" or "because it hit 500,000 miles" is an accounting habit, not an economics decision. The correct trigger is when the asset's going-forward maintenance CPM — modeled on a trailing repair curve — exceeds the ownership CPM of a replacement unit. A 2019 tractor with rising repair costs may reach that crossover at 450,000 miles; a well-PM'd 2020 unit may not reach it until 650,000. Replacing on age alone either scraps productive iron too early or keeps it too late. Both errors cost margin.

## How to apply

Build a lifecycle replacement model for each unit flagged for review:

```
Lifecycle replacement model (per unit):
  Trailing 12-month maintenance cost ($):    ______
  Trailing 12-month miles driven:            ______
  Current maintenance CPM:                   $ / mile

  Replacement unit cost (new or used):       $______
  Estimated financing cost / month:          $______
  Replacement unit warranty / CPM floor:     $______
  Breakeven miles to amortize purchase:      ______

  Crossover test:
    If current maint. CPM > replacement ownership CPM → replace
    If current maint. CPM < replacement ownership CPM → keep and re-check in 90 days
```

Additional signals that accelerate the crossover:
- Unplanned downtime rate > 10% of available days in trailing 90 days.
- Single repair event > 25% of the unit's annual depreciation value.
- Parts lead times making the unit unavailable for >5 days per repair.

**Do:**
- Build the model unit-by-unit, not fleet-average — replacement decisions are individual.
- Factor residual/trade value of the current unit as a credit in the replacement economics.
- Model used-truck acquisition CPM separately from new — the used-truck market moves with the freight cycle and the spread is material.

**Don't:**
- Make a replacement decision based on age, mileage milestone, or a vendor rep's recommendation without running the crossover test.
- Ignore downtime cost in the maintenance CPM — a truck that's off-road 15% of its schedule has a true CPM higher than its repair invoices show.

## Edge cases / when the rule does NOT apply

Private fleets governed by a corporate asset policy (fixed replacement cycles) are operating under a different constraint — the rule still informs pushback to that policy but does not override it unilaterally. Emergency replacement after a totaling accident bypasses the model by necessity.

## See also

- [`../agents/fleet-maintenance-specialist.md`](../agents/fleet-maintenance-specialist.md) — owns the trailing repair curve and downtime analysis.
- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the lifecycle CPM model and replacement economics.
- [`./preventive-maintenance-is-cheaper-than-the-breakdown.md`](./preventive-maintenance-is-cheaper-than-the-breakdown.md) — a strong PM program delays the crossover; the two rules are linked.

## Provenance

Lifecycle replacement modeling is standard fleet-management practice; the CPM crossover framework is consistent with methodology used in ATRI's annual operational cost report and fleet consulting practice.

---

_Last reviewed: 2026-06-05 by `claude`_
