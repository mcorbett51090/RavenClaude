---
scenario_id: 2026-06-08-store-run-on-new-car-gross
contributed_at: 2026-06-08
plugin: automotive-dealership
product: fixed-ops
product_version: "n/a"
scope: likely-general
tags: [fixed-ops, absorption, new-car-gross, fragility]
confidence: medium
reviewed: false
---

## Problem

A GM celebrated record new-car gross and under-invested in service, then margins compressed and the store swung to a loss. The risk: a store run on volatile front-end new-car gross has no durable floor; when front gross compresses, a low absorption rate exposes the whole overhead (§3 #1 #5).

## Context

- Store: single rooftop, volume brand, hot-market front grosses.
- Constraint: absorption = fixed-ops gross ÷ total fixed overhead; below 100% the showroom carries the overhead (§3 #5).
- The GM reasoned from the front-gross line, which was at a peak.

## Attempts

- Tried: **computed the absorption rate** (`automotive_dealership_calc.py absorption`). Outcome: absorption sat well below 100% — service covered only a fraction of overhead, so front gross was funding the building.
- Tried: **stress-tested front gross down to a normalized level.** Outcome: at normalized front grosses the store lost money — the peak had hidden the fragility (§3 #1).
- Tried: **traced the absorption shortfall** to labor rate and service retention. Outcome: under-invested service capacity and weak retention were the real gap (§3 #7).

## Resolution

The fix was a **fixed-ops investment plan (capacity + retention) to lift absorption**, treating front gross as upside rather than the foundation. The output was the absorption read, the normalized-gross stress test, and the fixed-ops action list.

**Action for the next consultant hitting this pattern:** **check absorption before celebrating front gross.** A store living on new-car gross is one market shift from a loss; absorption is the survival metric and fixed-ops is the engine. See Tree 1/2 and the `automotive_dealership_calc.py` `absorption` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
