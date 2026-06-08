---
scenario_id: 2026-06-08-fixed-ratio-mis-staffed
contributed_at: 2026-06-08
plugin: customer-support-cx-operations
product: staffing
product_version: "n/a"
scope: likely-general
tags: [staffing, occupancy, backlog-flow, workload]
confidence: medium
reviewed: false
---

## Problem

A team staffed by a fixed 'one agent per 75 tickets/day' ratio and alternated between idle agents and SLA breaches. The risk: a fixed ratio ignores handle time and occupancy and breaks the instant volume or AHT varies, so it mis-staffs in both directions (§3 #2).

## Context

- Channel: chat + voice with very different AHT.
- Constraint: staffing is workload (contacts × AHT) ÷ (interval × occupancy), and backlog is arrivals vs capacity (§3 #2 #5).
- The team reasoned from a single ratio.

## Attempts

- Tried: **recomputed staffing as workload-based** (`supportops_calc.py staffing`). Outcome: voice's higher AHT meant the ratio under-staffed voice and over-staffed chat.
- Tried: **set a target occupancy band** instead of implicit 100% (§3 #2). Outcome: the prior plan ran agents near saturation, lengthening AHT and feeding the backlog.
- Tried: **read the backlog as arrivals vs capacity** (`supportops_calc.py sla-backlog`). Outcome: a days-to-clear projection replaced 'work faster' (§3 #5).

## Resolution

The fix was **workload-based, occupancy-aware staffing by channel and interval** plus a flow-based backlog plan — not a single ratio. The output was the staffing model, the occupancy band, and the days-to-clear projection.

**Action for the next consultant hitting this pattern:** **staff to workload and occupancy, and read backlog as a flow.** A fixed ratio ignores AHT and occupancy; compute agents from contacts × AHT at a healthy occupancy band, and project the backlog from arrivals vs capacity. See Tree 2 and the `supportops_calc.py` `staffing` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
