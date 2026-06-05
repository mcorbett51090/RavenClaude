---
scenario_id: 2026-06-05-occupancy-slide-segment-recovery
contributed_at: 2026-06-05
plugin: senior-care-operations
product: census
product_version: "n/a"
scope: likely-general
tags: [occupancy, census, move-out, segment, sales-funnel]
confidence: medium
reviewed: false
---

## Problem

An assisted-living community's occupancy had slipped from the high-80s to the low-80s over four months and the executive director's reflex was a community-wide rate concession "to fill beds." The risk: a blanket discount erodes margin across *every* resident to fix a problem that — if it is concentrated in one unit type or driven by move-outs rather than thin demand — a blanket discount does not even address. The number was treated as a single point ("occupancy is down") instead of as a flow with a decomposable driver.

## Context

- Segment: assisted-living + a memory-care neighborhood, single building, ~90 units, independent operator.
- Constraint: census is a **flow** — occupancy(t) = occupancy(t-1) + move-ins − move-outs. A point-in-time occupancy number hides whether the slide is a move-in (sales/demand) problem or a move-out (retention/attrition) problem, and whether it is broad or segment-specific. The market itself was a tailwind, not a headwind: senior-housing occupancy rose through 2025 (18 consecutive quarters of gains) to ~89.1% overall and ~87.7% for assisted living in Q4 2025 — so a single building sliding *against* a rising market is an internal signal, not a demand story.
- The ED was reasoning from the aggregate number without segmenting unit type or splitting the move-in/move-out flow.

## Attempts

- Tried: **decomposed the slide before pricing anything** — segmented occupancy by unit type and split the flow into move-ins vs move-outs by month. Outcome: the decline was concentrated in memory care, and it was a **move-out** spike (avoidable transfers after two falls and a staffing-driven care-quality complaint), not a move-in shortfall. A community-wide discount would have spent margin on the AL side, which was fine.
- Tried: **ran a move-out root-cause split** (avoidable vs unavoidable — death / higher level of care are unavoidable; dissatisfaction / preventable decline are avoidable). Outcome: the avoidable share was the lever; the fix was a memory-care fall-prevention + staffing-stability intervention, not a price cut.
- Tried: **checked the sales funnel for the memory-care segment specifically** to confirm move-ins could backfill once the leak was stopped. Outcome: inquiry volume was healthy; the segment just needed the move-out bleed stopped and a targeted (not community-wide) sales push on the now-open MC units.

## Resolution

The recovery was a **segment-targeted** move-out-root-cause fix plus a memory-care-only sales plan — **not** a community-wide rate concession. Occupancy is a flow, and the driver was avoidable move-outs in one segment; pricing the whole building down would have burned AL margin to "fix" an MC retention problem. The output was a dated decomposition (occupancy by segment, move-in/move-out split, avoidable/unavoidable share) with a targeted action per leaf.

**Action for the next consultant hitting this pattern:** **decompose before you discount.** Segment occupancy by unit type, split the flow into move-ins vs move-outs, and split move-outs into avoidable vs unavoidable — *then* pick the lever. A community-wide rate concession is the most expensive, lowest-precision response to a number you have not yet decomposed. See [`../knowledge/senior-care-decision-trees.md`](../knowledge/senior-care-decision-trees.md) "Why Occupancy Is Declining" and the [`../scripts/senior_calc.py`](../scripts/senior_calc.py) `occupancy-revenue` mode for the revenue-at-stake arithmetic.

**Sources (retrieved 2026-06-05):**
- NIC — Occupancy Rate for Senior Living Communities Increased in 2025 (18 consecutive quarters; ~89.1% overall): https://www.nic.org/news-press/occupancy-rate-for-senior-living-communities-increased-in-2025-as-construction-stalled/
- NIC MAP — Senior Housing Occupancy Rises, inventory growth at record lows (2025): https://www.nicmap.com/blog/senior-housing-occupancy-rises-in-2q-2025-inventory-growth-at-record-lows/

Market occupancy figures are dated and segment-/region-dependent — treat as `[verify-at-use]` and validate against the building's own trailing census before any deliverable (§3 #8).
