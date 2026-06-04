---
name: kpi-dashboard-design
description: Lay out a staffing KPI dashboard so the most decision-relevant number is read first, every tile pairs with its partner metric, and a red number explains itself via drill-down. Reach for this when turning a scorecard spec into a dashboard layout (not the build — the design).
---

# Skill: KPI dashboard design

A scorecard defines the numbers; the dashboard decides what an operator sees in the first three seconds. This skill is about layout and information hierarchy, not instrumentation.

## Step 1 — Lead with the decision metric
The top-left tile is the KPI that answers the dashboard's reason for existing (fill rate, margin, or FTE-on-assignment, depending on the audience). Everything else supports it.

## Step 2 — Pair tiles physically
Fill rate sits beside time-to-fill; margin beside its bill/pay/burden breakdown; revenue-per-recruiter beside reqs-per-recruiter. Adjacency enforces the constitution's pairing rule visually (§3 #2, #3, #4) — a viewer can't read one without seeing its partner.

## Step 3 — Every tile shows value + delta + baseline
No bare numbers. Each tile: current value, the delta vs. baseline, and what the baseline *is* (prior period / SLA / target). A trend sparkline (8–12 periods) gives the seasonality context that a point-in-time number hides.

## Step 4 — Make red explain itself
A red tile must surface its top 1–2 drivers on hover/drill — the components from the scorecard's drill-down field. A red number with no visible driver generates a meeting; a red number with its driver generates an action.

## Step 5 — Segment selector, not segment blend
A filter for healthcare-travel / locum / allied / per-diem / education-school-based. Never show a cross-segment average as a headline — the seasonalities and benchmarks differ enough to make the blend meaningless.

## Step 6 — Surface the triggered action
The recommended action for the current band, in plain language, on or beside the tile. If the operator has to remember the playbook, the dashboard isn't doing its job.

## Step 7 — Mark soft numbers visibly
Benchmarks shown as comparison lines are labeled `[ESTIMATE]` if advisory-sourced. The client's own baseline is the solid line; the benchmark is dashed.

## Output
Feeds [`../../templates/staffing-dashboard-spec.md`](../../templates/staffing-dashboard-spec.md). Demo data: [`../../bi-report/data.json`](../../bi-report/data.json). For the actual build/instrumentation, route to `ravenclaude-core/data-engineer`; for the metric definitions, [`staffing-scorecard-build`](../staffing-scorecard-build/SKILL.md).
