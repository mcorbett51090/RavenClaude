# revenue-operations

The **lead-to-cash operations layer** that connects marketing, sales, and customer success into a
single, trusted revenue engine. This plugin's team helps you design your RevOps function, architect a
clean CRM-as-process, build a defensible forecast, and design comp and territory structures that drive
the behavior you actually want.

> **The one-line philosophy:** revenue operations is the operating system of GTM — it only works when
> every team is looking at the same pipeline, the same definitions, and the same source of truth. The
> RevOps team's job is to design that system and hold the line on it.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
| --- | --- |
| "Design our RevOps function / audit our GTM data model / assess RevOps maturity" | **revenue-operations** (`revops-lead`) |
| "Fix our CRM data / design the opportunity stage model / dedupe / validation rules" | **revenue-operations** (`crm-operations-architect`) |
| "Design our comp plan / allocate territories / set quota / model headcount capacity" | **revenue-operations** (`sales-comp-and-territory-analyst`) |
| "Build our forecast / define pipeline stages / fix pipeline accuracy" | **revenue-operations** (`pipeline-forecast-engineer`) |
| "Configure Salesforce objects / flows / Apex" | `salesforce` |
| "Post-sale health scores / churn risk / renewal analytics" | `customer-success-analytics` |
| "Product roadmap / why decisions / product metrics" | `product-management` |
| "Revenue plan / headcount budget / quota-to-revenue bridge" | `finance` |
| "Is this pipeline experiment statistically significant?" | `applied-statistics` |

## What's inside

- **4 agents** — `revops-lead`, `crm-operations-architect`, `sales-comp-and-territory-analyst`,
  `pipeline-forecast-engineer`.
- **3 skills** — `pipeline-hygiene-and-stage-definitions`, `forecasting-methodology`,
  `comp-and-territory-design`.
- **3 commands** — `/revenue-operations:design-pipeline-stages`,
  `:build-forecast`, `:audit-crm-hygiene`.
- **2 templates** — `stage-definition-doc`, `comp-plan-spec`.
- **Knowledge bank** — `knowledge/revops-decision-trees.md`: Mermaid trees for forecast-method
  selection, comp-plan shape, and lead-routing/assignment, plus a dated 2026 capability map.
- **6 best-practices**, **1 advisory hook** (flags missing exit-criteria, hard-coded comp figures,
  PII in plaintext, forecasts with no method), **`scripts/revops_calc.py`** (quota attainment,
  pipeline coverage, weighted/commit forecast, win rate, sales velocity).

## House opinions (the short list)

1. Stages are exit-criteria, not vibes.
2. One definition of pipeline — no shadow pipelines.
3. A forecast is a commitment, not a hope; it must name its methodology.
4. The comp plan is the strategy — design it deliberately.
5. Territory by data, not tenure.
6. CRM hygiene is a process, not a one-time cleanup.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
