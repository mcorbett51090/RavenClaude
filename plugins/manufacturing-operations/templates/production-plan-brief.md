# Production Plan — Brief

> Output of `production-planner` / the `mrp-and-production-planning` skill. A schedule with no capacity basis,
> no constraint reference, or an unvalidated BOM is not ready to release.

## 1. Demand & horizon

- **Demand / forecast:** <source, quantity, mix>
- **Horizon + planning bucket:** <e.g. 13 weeks, weekly buckets>
- **Reconciled in S&OP?** <yes/no — if no, reconcile before planning>

## 2. The constraint

- **Binding constraint:** <resource / cell>
- **Real sustainable rate:** <OEE-adjusted; route to shop-floor-and-oee-analyst if unknown>
- **Plans to infinite capacity?** <must be No>

## 3. Master schedule (MPS) + MRP

| End item | Qty | Bucket | Capacity-feasible? | Material-feasible? |
|---|---|---|---|---|
| <item> | | | <yes/no> | <yes/no vs as-built BOM> |

_MRP exception messages / phantom-shortage hunts: <notes>_

## 4. BOM integrity

- **Matches as-built?** <yes / where it drifted>
- **Effectivity / phantom items checked?** <notes>

## 5. Lot sizing

| Item | Rule (EOQ / fixed-period / lot-for-lot) | Setup-vs-holding trade named | Safety stock basis |
|---|---|---|---|
| <item> | | | <demand/lead-time variability + service level> |

## 6. S&OP gaps & options

| Gap (capacity / material / labor) | Option | Trade it makes |
|---|---|---|
| <gap> | <overtime / shift / lot change / date push> | <cost / lead time / service> |

## 7. Handoff to method teams

| What | Routed to |
|---|---|
| SMED / changeover reduction so smaller lots are economic | `process-improvement` |
| The statistical demand-forecast model / safety-stock math | `applied-statistics` |
| Material lead-time, supplier capacity, dual-sourcing | `procurement-sourcing` |
| The constraint's real rate / OEE-adjusted capacity | `shop-floor-and-oee-analyst` |

---

```
Status: ...
Files changed: ...
Constraint respected: ...
Assumptions stated: ...
Handoff to method teams: ...
Open questions: ...
Grounding checks performed: ...
```
