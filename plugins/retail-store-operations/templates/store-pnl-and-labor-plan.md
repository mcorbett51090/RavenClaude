# Store P&L and Labor Plan

> Output of `store-operations-lead` / the `store-labor-and-pnl` skill. A plan that doesn't land on a P&L line,
> doesn't schedule against traffic, or diagnoses shrink as one undifferentiated number is not ready to ship.

## 1. The store P&L walk

| Line | Plan | Actual | Gap ($) | Moved? |
|---|---|---|---|---|
| Sales | | | | |
| Gross margin ($ / %) | | | | |
| Labor % of sales | | | | |
| Shrink % | | | | |
| Controllable expense | | | | |
| **Four-wall contribution** | | | | |

_Name the single line that moved most and the dollar size of the prize._

## 2. Schedule-to-traffic labor model

| Daypart | Traffic | Conversion | Hours scheduled | Over / under vs. traffic |
|---|---|---|---|---|
| Open–mid | | | | |
| Peak | | | | <protect — don't cut> |
| Close | | | | |

- **Labor-% impact of the re-shape:** <points / dollars>
- **What you're trading:** <labor % vs. conversion — name it>

## 3. Shrink diagnosis

| Bucket | Likely driver | Evidence | Cheapest counter-measure |
|---|---|---|---|
| Operational (receiving/markdown/process) | | | |
| Theft (internal / external) | | | <surveillance → security-reviewer> |
| Vendor / admin (cost/count error) | | | |

_Most shrink is operational — rule out the cheap causes before cameras._

## 4. SOP changes

| SOP | Owner | Failure mode it prevents | Audit step |
|---|---|---|---|

## 5. Handoff

| What | Routed to |
|---|---|
| The planogram / assortment / markdown margin lever | `merchandising-analyst` |
| Replenishment / the stock-loss side of shrink | `inventory-and-replenishment-planner` |
| The online channel / ship-from-store economics | `ecommerce-dtc` |
| The labor / shrink / P&L dashboard | `data-platform` |
| Employee PII / surveillance / payment data | `ravenclaude-core/security-reviewer` + `data-governance-privacy` |

---

```
Status: ...
Files changed: ...
P&L impact: ...
Assumptions & data gaps: ...
Handoff to neighbours: ...
Open questions: ...
Grounding checks performed: ...
```
