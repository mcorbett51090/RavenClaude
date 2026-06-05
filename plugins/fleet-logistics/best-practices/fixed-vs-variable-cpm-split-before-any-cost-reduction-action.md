# Split Fixed vs. Variable CPM Before Any Cost-Reduction Action

**Status:** Absolute rule
**Domain:** Fleet cost analysis
**Applies to:** `fleet-logistics`

---

## Why this exists

Cost-per-mile is built from two structurally different cost pools: fixed costs that do not move with miles (depreciation, insurance, driver base pay, licensing) and variable costs that do (fuel, tires, maintenance, driver-mile pay). A cost-reduction action that works in one pool often worsens the other or has no effect. Cutting miles to reduce fuel spend (variable) raises the fixed CPM because the denominator shrinks. Adding a truck raises the fixed cost base before the revenue materializes. Confusing the two pools produces interventions that move cost in the wrong direction. Splitting the CPM before acting is the discipline that keeps the analysis honest.

## How to apply

Build the CPM split explicitly — do not present a blended CPM for any cost-reduction conversation:

```
CPM split template (per truck, per mile):
FIXED CPM:
  Depreciation or lease:         $___/mile
  Insurance (liability, cargo):  $___/mile
  Driver base / guarantee:       $___/mile
  Permits, licensing, IFTA base: $___/mile
  Fixed overhead allocation:     $___/mile
  ─────────────────────────────────────────
  Total fixed CPM:               $___/mile

VARIABLE CPM:
  Fuel (net of FSC recovery):    $___/mile
  Tires:                         $___/mile
  Maintenance (PM + unplanned):  $___/mile
  Driver-per-mile pay:           $___/mile
  Tolls, scales:                 $___/mile
  ─────────────────────────────────────────
  Total variable CPM:            $___/mile

TOTAL CPM:                       $___/mile
```

Decision gate: before recommending a cost action, ask "which pool does this touch?"
- If the action reduces variable cost → project at current and higher mileage (scale test).
- If the action reduces fixed cost → check whether miles or asset count changes.
- If the action increases one pool to reduce the other → net the tradeoff explicitly.

**Do:**
- Update the CPM split quarterly; fixed cost per mile shifts as mileage and depreciation schedules change.
- Use the variable CPM floor as the minimum rate to accept on a spot load — at least variable costs must be covered.
- In any fleet-expansion or fleet-reduction decision, model the fixed-CPM impact of the change in asset count before proceeding.

**Don't:**
- Present a blended CPM without the split when a cost-reduction action is under discussion — the split is what makes the action testable.
- Attribute a variable cost (e.g., a tire blowout) to the fixed pool or vice versa — the split only works if the categories are correct.

## Edge cases / when the rule does NOT apply

Owner-operators with no employees and a simple single-truck operation often run an all-in cash-flow view rather than a formal split; the discipline still applies conceptually, but the formalism can be simplified to "fixed per month ÷ monthly miles" vs. "variable per mile."

## See also

- [`../agents/logistics-cost-analyst.md`](../agents/logistics-cost-analyst.md) — owns the CPM split model and the quarterly update.
- [`../agents/fleet-engagement-lead.md`](../agents/fleet-engagement-lead.md) — uses the split as the diagnostic frame during the engagement read.
- [`./cost-per-mile-is-the-master-number-build-it-bottom-up.md`](./cost-per-mile-is-the-master-number-build-it-bottom-up.md) — the parent rule; the fixed/variable split is the structural discipline that gives the bottom-up build its analytical power.

## Provenance

Codifies standard cost-accounting discipline applied to trucking; the fixed/variable decomposition is the foundation of ATRI's operational cost methodology and every carrier cost-reduction consulting framework.

---

_Last reviewed: 2026-06-05 by `claude`_
