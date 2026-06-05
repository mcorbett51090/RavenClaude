---
scenario_id: 2026-06-05-breakeven-vs-input-cost-spike
contributed_at: 2026-06-05
plugin: precision-agriculture
product: farm-economics
product_version: "n/a"
scope: likely-general
tags: [breakeven, input-cost, corn, margin, per-acre]
confidence: medium
reviewed: false
---

## Problem

A corn grower watched the cash bid fall below where it could pencil and wanted to know the one number that actually mattered: at this year's input cost, what price does a bushel have to clear to break even — and is that price reachable in the current market? The risk was planting the same acres on last year's mental breakeven, not the one that reflects the input-cost stack the grower is actually committing to this spring.

## Context

- Segment: row-crop, dryland + some irrigated, ~1,800 acres corn-soybean rotation, independent operator who markets his own grain.
- Constraint: 2025 was a published squeeze year — the USDA-forecast **average cost to grow corn was ~$897/acre** while the **market-year-average farm price forecast was cut to ~$3.90/bu**, below most breakeven estimates [verify-at-use, 2025 figures]. The grower's instinct ("prices are fine") was anchored on a prior, higher-price year.
- The grower had a whole-farm cost number but no **per-acre, by-field** breakeven — so the money-losing fields were invisible inside the average (§3 #4).

## Attempts

- Tried: computed the cost-side breakeven the only honest way — **total cost per acre ÷ realistic yield = breakeven price**, run **per field**, not whole-farm. On a high-productivity field at $897/acre and a 230 bu/acre APH, breakeven is ~$3.90/bu; on a weaker field at the same cost and a 175 bu/acre yield, breakeven is ~$5.13/bu [ESTIMATE — illustrative]. The weak field was underwater at the current bid; the strong field was at the knife's edge. Outcome: the by-field split surfaced exactly which acres lost money — the whole-farm average had hidden it.
- Tried: also computed the **breakeven yield at the current cash price** (cost per acre ÷ price) so the grower could see how many bushels each field had to clear to cover cost — a second framing of the same squeeze that operators read faster.
- Tried: ran the cost stack against the **economic-optimum, not maximum-yield** lens (§3 #1) — trimming the last, lowest-return units of N and seed on the weak field lowered cost per acre enough to pull its breakeven back toward the reachable band, rather than chasing a top-end yield that the price couldn't pay for.

## Resolution

The deliverable was a **per-field breakeven table** (cost/acre, realistic yield, breakeven price, and breakeven yield at the current bid) with the two underwater fields flagged for either a rotation switch or an input-cost trim, not a uniform whole-farm "hope prices recover." The grower entered the season knowing the exact price each field needed — and which fields needed a plan, not a prayer.

**Action for the next consultant hitting this pattern:** **breakeven is per field, on this year's cost stack — never the whole-farm average on last year's costs.** Compute both framings (breakeven price = cost/acre ÷ yield; breakeven yield = cost/acre ÷ price) so the grower can read it either way, and always test the cost stack at the economic optimum before declaring a field underwater (§3 #1, #4). The [`../scripts/ag_calc.py`](../scripts/ag_calc.py) `breakeven` mode does this arithmetic per field.

**Sources (retrieved 2026-06-05):**
- NCGA — High Production Cost Series (2025 cost-of-growing-corn framing): https://ncga.com/stay-informed/media/the-corn-economy/article/2025/08/high-production-cost-series-part-1
- Purdue Center for Commercial Agriculture — 2025 Crop Cost and Return Guide (low/high-productivity breakeven): https://ag.purdue.edu/commercialag/home/paer-article/2025-purdue-crop-cost-and-return-guide/
- farmdoc daily — Revised 2025 Crop Budgets (nonland-cost breakeven range): https://farmdocdaily.illinois.edu/2025/01/revised-2025-crop-budgets.html
- Farm Progress — Breakeven prices crucial for crop decisions: https://www.farmprogress.com/farm-business/breakeven-prices-crucial-for-crop-decisions-as-corn-soybean-markets-fluctuate

All cost/price figures are 2025-season, region-dependent, and move constantly — treat every number as `[verify-at-use]` and recompute against the grower's own budget and current cash bid before any deliverable (§3 #8).
