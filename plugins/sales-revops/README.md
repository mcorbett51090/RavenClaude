# sales-revops

A **Sales & Revenue Operations specialist team** for a RevOps leader, sales ops analyst, or founder accountable for pipeline, forecast accuracy, and quota attainment. It reads pipeline as coverage-against-quota not a single number, forecasts from stage-weighted history not gut, designs quota to capacity, and treats win-rate and sales-cycle as a funnel system.

> Inherits the [`ravenclaude-core`](../ravenclaude-core/) protocols (claim-grounding, structured output, decision review). Motion-explicit, segment-flexible (SMB | mid-market | enterprise | PLG | hybrid).

## What you get

| Surface | Contents |
|---|---|
| **4 agents** | `revops-lead`, `pipeline-forecast-analyst`, `funnel-conversion-strategist`, `quota-territory-architect` |
| **5 skills / commands** | `build-forecast` · `read-pipeline-coverage` · `diagnose-funnel` · `model-velocity` · `design-quota` |
| **4-file knowledge bank** | KPI glossary · unit economics · 2025–2026 context · Mermaid decision trees |
| **4 templates** | scorecard · exec readout · forecast-worksheet.md · quota-capacity-model.md |
| **1 advisory hook** | flags anti-patterns (unbaselined metric, unsourced benchmark, customer/rep PII) in generated deliverables |
| **`scripts/revops_calc.py`** | stdlib calculator — `coverage` · `forecast` · `funnel` · `velocity` · `quota-capacity` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install sales-revops@ravenclaude
```

## Quickstart

> "Our forecast keeps missing — where's the gap?"

The `revops-lead` scopes the problem, routes to `pipeline-forecast-analyst` (or a sibling specialist), and synthesizes a ranked action plan with owners, dates, and expected metric movement.

## What it is not

a CRM administrator, a sales-coaching authority, or a finance/RevRec function. It does not close deals, set GAAP revenue recognition, or store customer PII. Revenue-recognition and legal questions route to the qualified authority.
