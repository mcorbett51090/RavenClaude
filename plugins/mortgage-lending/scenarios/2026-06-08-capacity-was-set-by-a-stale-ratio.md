---
scenario_id: 2026-06-08-capacity-was-set-by-a-stale-ratio
contributed_at: 2026-06-08
plugin: mortgage-lending
product: cycle-capacity
product_version: "n/a"
scope: likely-general
tags: [cycle-time, capacity, rate-cycle, staffing]
confidence: medium
reviewed: false
---

## Problem

A shop staffed by a fixed 'loans per processor' headcount rule and kept missing throughput as cycle time crept up. The risk: loans-per-processor is a function of cycle days, not a static ratio — when the cycle lengthens, each processor carries open loans longer and real capacity falls, so a fixed ratio silently over-promises (§3 #2 #4).

## Context

- Channel: wholesale, refi-heavy as rates moved.
- Constraint: capacity = processors × loans-per-processor-at-cycle, and loans-per-processor falls as cycle lengthens (§3 #4).
- The shop reasoned from the legacy ratio.

## Attempts

- Tried: **measured app-to-close cycle and dwell by stage.** Outcome: cycle had grown materially, concentrated in one bottleneck stage (§3 #2).
- Tried: **recomputed capacity as a function of the actual cycle** (`mortgage_lending_calc.py cycle-capacity`). Outcome: real capacity was well below the ratio's promise — the staffing gap was structural.
- Tried: **planned to the rate-swing breakeven, not the peak** (§3 #7). Outcome: a staffing plan that flexes with the cycle instead of a fixed number.

## Resolution

The fix was to **staff to the measured cycle and the rate-swing breakeven — and clear the bottleneck stage — not to the legacy ratio**. The output was the cycle/dwell read, the cycle-tied capacity, and the swing-aware staffing plan, with no borrower NPI in the deliverable.

**Action for the next consultant hitting this pattern:** **staff to the cycle, not a fixed loans-per-processor ratio.** Capacity falls as cycle lengthens; recompute it from the actual cycle and plan for the rate swing, not the peak. See Tree 2 and the `mortgage_lending_calc.py` `cycle-capacity` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
