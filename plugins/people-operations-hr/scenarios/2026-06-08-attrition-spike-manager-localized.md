---
scenario_id: 2026-06-08-attrition-spike-manager-localized
contributed_at: 2026-06-08
plugin: people-operations-hr
product: attrition
product_version: "n/a"
scope: likely-general
tags: [attrition, retention, segmentation, manager-quality, engagement]
confidence: medium
reviewed: false
---

## Problem

A 600-person scale-up saw annualized turnover jump and leadership's reflex was a company-wide retention bonus "to stop the bleeding." The risk: a blanket spend treats every employee as a flight risk to fix a problem that — if concentrated in one org or driven by a single manager — a blanket bonus does not even address. The number was read as a single point ("attrition is up") instead of split, segmented, and costed.

## Context

- Scope: a single product org inside a larger company; mixed IC + manager population.
- Constraint: turnover is two different things — regretted (a loss to recover) and non-regretted (often intended managing-out). The company number blended them, and it was not segmented by team, manager, or tenure cohort (§3 #1, #7).
- Leadership reasoned from the aggregate without splitting regretted/non-regretted or localizing the spike.

## Attempts

- Tried: **split regretted vs non-regretted before costing anything.** Outcome: roughly half the rise was non-regretted (a deliberate performance cleanup), so the recoverable loss was far smaller than the headline implied.
- Tried: **segmented the regretted exits by team, manager, and tenure cohort** (`people_calc.py attrition --segment-*`). Outcome: the regretted spike was concentrated in two teams under one newly-promoted manager with an extreme span of control — a manager/span problem, not a company comp problem (§3 #7).
- Tried: **crossed the segment against the engagement pulse.** Outcome: the same teams showed the lowest manager-effectiveness favorability — a leading indicator that had been hidden by the company-wide eNPS (§3 #4).

## Resolution

The fix was a **targeted** manager-coaching + span-of-control intervention on two teams, plus a re-leveling of the affected ICs to band — **not** a company-wide retention bonus. Costing only the regretted, localized exits made the intervention's ROI legible. The output was a dated decomposition (regretted/non-regretted split, segment deltas, replacement cost) with a targeted action per leaf.

**Action for the next consultant hitting this pattern:** **split, segment, and cost before you spend.** Split regretted from non-regretted, localize the regretted spike to a team/manager/cohort, and price only the recoverable loss — *then* pick the lever. A company-wide retention spend is the most expensive, lowest-precision response to a turnover number you have not yet decomposed. See [`../knowledge/people-ops-decision-trees.md`](../knowledge/people-ops-decision-trees.md) Tree 1 and the [`../scripts/people_calc.py`](../scripts/people_calc.py) `attrition` mode.

Benchmark turnover figures are industry-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the org's own trailing data before any deliverable (§3 #8).
