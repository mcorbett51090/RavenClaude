---
scenario_id: 2026-06-05-prime-cost-blowout
contributed_at: 2026-06-05
plugin: restaurant-operations
product: unit-economics
product_version: "n/a"
scope: likely-general
tags: [prime-cost, food-cost, labor, theoretical-vs-actual, four-wall]
confidence: medium
reviewed: false
---

## Problem

A single-unit casual full-service restaurant was "busy but broke" — sales were flat-to-up year over year, yet the four-wall took home almost nothing. The operator's instinct was a price increase across the board. Prime cost (food + labor) was running in the **high 60s to ~70% of revenue**, well above the 60–65% range that full-service should hold [verify-at-use], and nobody could say which half was the driver.

## Context

- Segment: casual, full-service, independent single unit. No theoretical food cost on file — food cost was "what the invoices added up to last month."
- Constraint: the POS tracked sales and labor punches but recipes weren't costed, so actual food cost couldn't be compared to a recipe-derived theoretical (§3 #2). Labor was scheduled by habit, not against a daypart sales forecast (§3 #4).
- The operator conflated "prime cost is high" (the master-number symptom) with "I need to raise prices" (one lever, often the wrong first one — §3 #3). Classic single-cause story.

## Attempts

- Tried: read **prime cost first**, then split it into food vs labor before touching anything (§3 #1, the read-prime-cost skill). Result: labor was roughly in band for the segment; **food cost was the outlier**, several points high — so a blanket price increase would have masked a food-cost control problem, not fixed it.
- Tried: built a theoretical food cost from the top-selling recipes and compared to actual (§3 #2, the close-the-food-cost-gap skill). The actual-minus-theoretical gap decomposed into **portioning drift on a few high-volume plates, over-prep waste on prep-ahead items, and one supplier's quiet price creep** — in that order of size. Result: reframed from "raise prices" to "close the theoretical gap on the items that move."
- Tried: spot-checked comps/voids — a creeping void rate on one terminal was a smaller, separate leak (§3 #6). Result: tightened void authorization.

## Resolution

The blowout was **mostly a food-cost-control gap (portioning + waste) against an uncosted menu**, not a pricing problem and not labor. The fix was operational: cost the recipes, set a theoretical target, retrain portioning on the high-volume plates, fix the prep-ahead par, and renegotiate the one creeping supplier — then reprice only the items that genuinely couldn't carry their margin (§3 #3, #5). Prime cost moved back toward band because the **denominator-and-control** work was done before the price lever.

**Action for the next consultant hitting this pattern:** lead with prime cost, then split food vs labor **before** recommending any lever — a blanket price increase on a food-cost-control problem just hides the leak and risks demand. Build a theoretical food cost; the actual-vs-theoretical gap is where the money is, not the invoice total (§3 #2). Decompose the gap (portioning / waste / price / theft) before negotiating with anyone.

**Sources (retrieved 2026-06-05):** prime-cost range + full-service food-cost average — 7shifts *Restaurant Prime Cost Guide* (https://www.7shifts.com/blog/restaurant-prime-cost-guide/) and Toast *Restaurant Payroll Percentage* (https://pos.toasttab.com/blog/on-the-line/restaurant-payroll-percentage). Specific figures are segment-dependent; treat any number as `[ESTIMATE]` and validate against the unit's actual P&L (§3 #8).
