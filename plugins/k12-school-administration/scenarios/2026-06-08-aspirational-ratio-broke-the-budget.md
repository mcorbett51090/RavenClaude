---
scenario_id: 2026-06-08-aspirational-ratio-broke-the-budget
contributed_at: 2026-06-08
plugin: k12-school-administration
product: staffing
product_version: "n/a"
scope: likely-general
tags: [staffing-ratio, budget, per-pupil, retention]
confidence: medium
reviewed: false
---

## Problem

A principal promised a lower student:teacher ratio for the fall without modeling it against the budget. The risk: a staffing ratio is an expense commitment — set as an aspiration untied to the funded envelope, it can require FTE and salary the budget can't cover, forcing a mid-year cut (§3 #3).

## Context

- Organization: district middle school, salary is the largest line.
- Constraint: teachers needed = enrollment ÷ ratio; cost = teachers × avg teacher cost (§3 #3).
- The principal reasoned from the desired ratio alone.

## Attempts

- Tried: **modeled the ratio into FTE and salary cost** (`k12_school_administration_calc.py staffing-ratio`). Outcome: the promised ratio required several more FTE than the budget funded — a large dollar variance.
- Tried: **re-based on the realistic funded enrollment.** Outcome: the affordable ratio was higher than promised; the gap was a budget reality, not a choice (§3 #1 #3).
- Tried: **considered per-pupil re-allocation to close part of the gap** by directing dollars to the highest-need grades (§3 #4).

## Resolution

The response was a **budget-fit ratio with targeted per-pupil allocation to the highest-need sections**, not a blanket promise — and a retention focus to protect the FTE already funded (§3 #7). The output was the FTE/cost variance and the allocation plan.

**Action for the next consultant hitting this pattern:** **fit the staffing ratio to the budget envelope before promising it.** A ratio is an expense commitment; model FTE and dollar variance against funded enrollment, and allocate per-pupil to need. See Tree 2 and the `k12_school_administration_calc.py` `staffing-ratio` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
