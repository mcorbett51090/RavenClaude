# people-operations-hr

A **People Operations / HR specialist team** for an HRBP, People-Ops leader, talent leader, or founder who owns a People metric — headcount, attrition, comp spend, or engagement. It quantifies attrition cost and cause before acting, pays to a defensible band rather than the counteroffer, treats time-to-fill and quality-of-hire as a hiring **system**, and reads engagement segmented as a leading indicator of regretted exits.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Function-explicit, stage-flexible (startup | scale-up | enterprise | nonprofit | agency).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `people-ops-lead` (orchestrator), `talent-acquisition-strategist`, `total-rewards-comp-analyst`, `people-analytics-engagement-specialist` |
| **5 skills / commands** | `diagnose-attrition`, `model-hiring-plan`, `design-comp-bands`, `run-pay-equity-review`, `read-engagement-signals` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 benchmark/regulatory context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · engagement brief · hiring-plan tracker |
| **1 advisory hook** | flags People-Ops anti-patterns (unbaselined metric, unsourced benchmark, employee PII) in generated deliverables |
| **`scripts/people_calc.py`** | stdlib calculator — `attrition` · `hiring-plan` · `comp-band` · `pay-equity` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install people-operations-hr@ravenclaude
```

## Quickstart

> "Our regretted attrition jumped this quarter — where and why?"

The `people-ops-lead` scopes whether the problem is comp, manager, growth, or workload, routes to `people-analytics-engagement-specialist` for the segmented read and replacement-cost, and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

Not an HRIS/ATS/payroll system, not an employment-law authority, not a benefits broker. It does not make termination decisions, give legal advice, or store employee PII. Legal/regulatory determinations route to qualified counsel.
