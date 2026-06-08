---
scenario_id: 2026-06-08-quota-miss-was-territory-design
contributed_at: 2026-06-08
plugin: sales-revops
product: quota
product_version: "n/a"
scope: likely-general
tags: [quota, territory, attainment-distribution, capacity]
confidence: medium
reviewed: false
---

## Problem

Half an AE team missed quota and leadership prepared a performance-management plan. The risk: under-attainment that's actually a quota-design or territory-imbalance problem gets misread as rep performance, churning good reps and leaving the real cause untouched (§3 #4 #7).

## Context

- Motion: enterprise field sales, named-account territories.
- Constraint: attainment variance can come from capacity (quota too high for ramped capacity) or territory design (unequal TAM/account quality), not just rep skill (§3 #4 #7).
- Leadership reasoned from the raw miss list.

## Attempts

- Tried: **read the attainment distribution** (P25/P50/P75) before acting. Outcome: the *median* sat well below 100% — a structural signal, not a few weak reps.
- Tried: **refit quota to ramped capacity** (`revops_calc.py quota-capacity`). Outcome: the top-down quota exceeded what the median ramped rep could produce — a design error.
- Tried: **scored territory balance** on TAM and named-account quality. Outcome: the 'underperformers' clustered in low-TAM territories — design, not skill (§3 #7).

## Resolution

The response split correctly: **refit quota to capacity and rebalance territories**, then performance-manage only the reps who still lagged in balanced territories — not a blanket PIP. The output was the attainment distribution, the capacity-tied quota, and the territory-balance read.

**Action for the next consultant hitting this pattern:** **read the attainment distribution and check capacity/territory before performance-managing.** A median far below 100% is a design problem; isolate it from rep skill with a capacity model and a territory-balance read. See Tree 3 and the `revops_calc.py` `quota-capacity` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
