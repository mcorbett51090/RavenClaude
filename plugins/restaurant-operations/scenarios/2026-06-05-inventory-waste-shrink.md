---
scenario_id: 2026-06-05-inventory-waste-shrink
contributed_at: 2026-06-05
plugin: restaurant-operations
product: inventory
product_version: "n/a"
scope: likely-general
tags: [inventory, waste, shrink, theoretical-food-cost, par, comps-voids]
confidence: medium
reviewed: false
---

## Problem

A multi-unit fast-casual brand had one store whose food cost ran several points above its comparable siblings on the same menu and the same supplier pricing. The GM blamed "vendor prices," but the same prices applied across every unit — so price couldn't explain a **store-specific** gap. The driver turned out to be **waste and shrink**: over-prep thrown out at close, spoilage from loose par levels, and unrecorded comps/voids masking give-aways as cost.

## Context

- Segment: fast-casual, multi-unit (same menu, same vendor contracts), one laggard store.
- Constraint: theoretical food cost existed at the brand level, so actual-vs-theoretical could be computed per store (§3 #2) — but the laggard store had no waste log and loose pars, so the gap had nowhere to be seen until it landed on the P&L.
- The GM conflated "my food cost is high" with "vendors raised prices" — impossible when siblings on identical pricing held band. **Multi-unit variance is the signal** (§3 #7): the spread between this store and its comparable best-quartile siblings was the entire finding.

## Attempts

- Tried: **ranked the store against its comparable siblings**, normalized for format and daypart (§3 #7, the rank-multi-unit skill), then decomposed its actual-vs-theoretical food-cost gap (§3 #2, the close-the-food-cost-gap skill). Sources of the gap, largest first: **over-prep waste at close, spoilage from too-high pars, and comps/voids recorded as cost** rather than as give-aways. Result: reframed from "negotiate vendor pricing" (impossible — chain-wide contract) to "fix this store's prep discipline, par levels, and comp/void control."
- Tried: instituted a **waste log + reorder pars** keyed to forecasted demand, and made **comps/voids a tracked control** with an authorizer (§3 #6) so give-aways stopped hiding inside food cost. Result: closed most of the waste/spoilage leak; comp/void rate became visible and dropped.
- Tried: mapped the **top-quartile siblings' practices** onto the laggard (§3 #7) rather than inventing a new program. Result: the laggard converged toward its cohort.

## Resolution

The store-specific food-cost gap was **waste + shrink + untracked comps/voids**, not vendor pricing (which was chain-wide and therefore couldn't be the variance driver). The fix was operational discipline — waste log, demand-keyed pars, and comp/void control with an authorizer — guided by ranking the store against its own comparable cohort and copying the best quartile's practices.

**Action for the next consultant hitting this pattern:** when **one** multi-unit store lags on a chain-wide menu/price, the variance is almost never the shared input (price) — it's store-level execution. Rank the laggard against comparable siblings, normalize for format/daypart (§3 #7), decompose actual-vs-theoretical (§3 #2), and treat **comps/voids/waste as a control system, not noise** (§3 #6). Copy the top quartile; don't reinvent.

**Sources (retrieved 2026-06-05):** multi-unit prime-cost / variance framing — Tris *Restaurant Prime Cost Benchmarks at 10, 20, and 50 Locations* (https://wearetris.com/2026/05/01/restaurant-prime-cost-benchmark-multi-unit-locations/); food-cost actual-vs-theoretical + range — VantaInsights *Restaurant Food Cost Percentage* (https://vantainsights.com/insights/restaurant-food-cost-percentage). COGS/variance figures are segment- and store-dependent; treat any specific number as `[ESTIMATE]` and validate against the unit's actual P&L (§3 #8).
