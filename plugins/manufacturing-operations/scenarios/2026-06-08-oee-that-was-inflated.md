---
scenario_id: 2026-06-08-oee-that-was-inflated
contributed_at: 2026-06-08
plugin: manufacturing-operations
product: oee
product_version: "unknown"
scope: likely-general
tags: [oee, denominators, six-big-losses, bottleneck, toc, takt]
confidence: high
reviewed: false
---

## Problem

A plant reported a line OEE of 85% to management every week, yet it was missing roughly a third of its ship dates. The number and the reality were in open contradiction, and trust in the metric had collapsed — operators called it "the management number." Meanwhile a six-figure capital request was on the table to add a second packaging machine, justified by "the packaging cell is our slow point."

## Constraints context

- Discrete assembly, three cells in series: fabrication → assembly → packaging.
- The "ideal cycle time" used in the OEE Performance term had been set years earlier to a marketing spec, not the demonstrated best repeatable rate — it was sandbagged, so Performance always looked near-perfect.
- Long machine-clean changeovers were being logged as "planned downtime" and excluded from the Availability denominator entirely.

## Attempts

- Tried: trending the 85% harder and setting an 88% target. Failed — chasing a gamed number changed nothing on the floor and deepened the operators' cynicism.
- Tried: approving the packaging machine to fix the "slow cell." Held — before spending, we followed the WIP: it was piling up in front of *assembly*, not packaging. Packaging was starved, not slow.
- Tried: rebuilding OEE with honest denominators — the demonstrated ideal cycle time and changeovers counted as the unplanned downtime they were. Recomputed OEE on the assembly constraint came out near 52%, and the six-big-losses Pareto put minor stops + changeover at assembly as the dominant loss. This matched reality.

## Resolution

The constraint was assembly, not packaging; the capital request was paused. Exploiting the assembly constraint (attacking the minor-stops and changeover losses the honest Pareto exposed, and subordinating the other cells to its rate) lifted real throughput enough to recover the ship dates without the second packaging machine. OEE was re-baselined with stated denominators so the number finally tracked the plant's actual performance.

## Lesson

An OEE figure with undefined denominators (sandbagged ideal cycle time, changeovers hidden as "planned downtime") is theater — and it points capital at the wrong cell. Define the denominators, follow the WIP to the real bottleneck (Theory of Constraints), and exploit the constraint before you buy capacity for a non-bottleneck.
