---
scenario_id: 2026-06-05-nutrient-budget-overspend
contributed_at: 2026-06-05
plugin: precision-agriculture
product: agronomy
product_version: "n/a"
scope: likely-general
tags: [fertility, soil-test, nitrogen, removal-rate, nutrient-budget]
confidence: medium
reviewed: false
---

## Problem

A grower's fertility line was the biggest controllable cost on the budget and it had crept up year over year, but the program was anchored on "what we did last year plus a little" rather than on current soil tests and crop removal. The risk was double: over-applying where soil-test levels were already adequate (cost with no yield return), and applying nitrogen at the agronomic maximum instead of the economic optimum — especially dangerous in a year of high N prices and tight margins (§3 #1, #5).

## Context

- Segment: row-crop, ~2,400 acres corn-soybean, fertility applied largely uniform by field, soil tests on a ~4-year grid but not driving the rate.
- Constraint: the **economic** optimum N rate is well below the **agronomic** optimum — in 2025 extension work, an agronomic maximum near ~300 lb N/acre corresponded to an economic optimum closer to ~150 lb N/acre on the cited site [verify-at-use, site-specific], and 2025 optimum N rates ran roughly **~24% below 2024** as N prices rose against tight margins. The grower's "rear-view" program had no mechanism to track that move.
- Phosphorus and potassium were applied without anchoring to **nutrient-removal rates** (lb of nutrient removed per bushel × yield), so build/maintenance decisions were guesses, not a budget.

## Attempts

- Tried: rebuilt the fertility budget **bottom-up from current soil tests + crop removal**, not history (§3 #5). For P and K, removal rate × realistic yield sets the maintenance floor; soil-test level sets whether the field is in build, maintain, or draw-down — three different rate answers the uniform program had collapsed into one.
- Tried: separated the **agronomic vs economic optimum N** explicitly and set the rate at the economic optimum where the marginal bushel from the last unit of N stops paying for that unit at the current N price and corn price (§3 #1) — recomputed at this year's N price, not last year's.
- Tried: flagged the residual-N opportunity — measuring residual soil inorganic N going into the next season to refine (and often lower) the N rate, rather than re-applying a full rate on top of carryover.

## Resolution

The deliverable was a **by-field fertility budget driven by soil test + removal rate**, with N set at the economic (not agronomic) optimum at the current price, and the over-applied adequate-test fields pulled back to maintenance — freeing budget without risking yield. The grower's takeaway: **fertility is a data-driven budget anchored on removal and current tests, not a rear-view program; and N is set at the economic optimum, which moves every year with price.**

**Action for the next consultant hitting this pattern:** anchor P and K on **nutrient-removal rate × realistic yield** plus current soil-test level (build / maintain / draw-down), and set **N at the economic optimum at this year's price**, not the agronomic maximum and not last year's rate. Check residual N before adding a full rate. The [`../skills/build-fertility-from-data/SKILL.md`](../skills/build-fertility-from-data/SKILL.md) skill drives this; the over-application is exactly the §4 anti-pattern the team flags.

**Sources (retrieved 2026-06-05):**
- U. of Minnesota Extension — _Updated corn nitrogen rates: profit vs yield_ (economic vs agronomic optimum; 2025 vs 2024 rate move): https://blog-crop-news.extension.umn.edu/2025/10/updated-corn-nitrogen-rates-regional.html
- Iowa State Integrated Crop Management — _Residual soil nitrogen from crop year 2025: how might it affect 2026 nitrogen needs?_: https://crops.extension.iastate.edu/post/residual-soil-nitrogen-crop-year-2025-how-might-it-affect-2026-nitrogen-needs
- Iowa State Research — _Ideal nitrogen fertilizer rates in Corn Belt have been climbing for decades_: https://research.iastate.edu/2025/03/03/ideal-nitrogen-fertilizer-rates-in-corn-belt-have-been-climbing-for-decades-study-shows/

N rates, the agronomic-vs-economic gap, and removal rates are region-, crop-, and price-dependent and move every season — treat every figure as `[verify-at-use]` and recompute against the grower's own soil tests, yield goals, and current N and grain prices (§3 #5, #8).
