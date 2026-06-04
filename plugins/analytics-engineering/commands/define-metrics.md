---
description: "Define metrics once in the semantic layer with explicit grain and filters; expose one contract to BI."
argument-hint: "[drifting/undefined metrics]"
---

You are running `/analytics-engineering:define-metrics`. Use `semantic-layer-engineer` + the `semantic-metrics-layer` skill.

## Steps
1. Pin each metric's grain + filters; define as metrics-as-code.
2. Model entities/dimensions to prevent fan-out.
3. Expose one contract for all BI; route significance to applied-statistics.
4. Emit (from `templates/metric-definition.md`) + Structured Output block.
