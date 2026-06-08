---
description: "Break down OEE (availability × performance × quality) with stated denominators, compare takt to cycle time, and find the binding constraint via Theory of Constraints."
argument-hint: "[line/cell + run time, downtime, output, scrap + ideal cycle time if known]"
---

You are running `/manufacturing-operations:analyze-oee`. Use `shop-floor-and-oee-analyst` + the `oee-and-throughput` skill.

## Steps
1. Pin the denominators: the ideal cycle time and the planned-vs-unplanned downtime split. If they're undefined, define them first — don't quote an undefined OEE.
2. Compute Availability × Performance × Quality and the six-big-losses Pareto.
3. Compare takt (available time ÷ demand) to measured cycle time; read the gap.
4. Identify the binding constraint (follow the WIP pile / the starved downstream); confirm it's actually the constraint before recommending any optimization.
5. Give the exploit → subordinate → elevate steps at the constraint; flag any non-bottleneck "improvement" as a mirage.
6. Route the deep fix: SMED/kaizen at the constraint → process-improvement; gauge-trust/variation-significance → applied-statistics; re-plan to the rate → production-planner.
7. Emit the OEE breakdown + the Structured Output block (with `Constraint respected:` and `Handoff to method teams:`).
