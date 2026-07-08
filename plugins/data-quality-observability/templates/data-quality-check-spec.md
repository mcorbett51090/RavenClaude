# Data-quality check spec — <dataset-name>

> The one-page spec captured **before** writing checks. Pairs with
> [`data-incident-runbook.md`](data-incident-runbook.md) (what to do when a check fires).

**Owner:** <name / on-call rotation> · **Date:** <YYYY-MM-DD> · **Tool:** <dbt tests / dbt-expectations / Great Expectations / Soda / Elementary / managed platform> · **Status:** draft / approved / built

## Dataset & grain
- **What this dataset is:** <table/model and what one row represents>
- **Grain / primary key:** <e.g. one row per order · `order_id`>
- **Consumers:** <dashboards / models / exports / downstream teams that rely on it — a contract with no named consumer is guessing>

## Data contract (the producer-boundary guarantee)
- **Schema:** <columns · types · nullability · enum domains>
- **Semantics:** <what each key column means · units · valid ranges · referential relationships>
- **Freshness expectation:** <e.g. "≤ 2h behind source `ordered_at`">
- **Volume expectation:** <e.g. "daily count within ±20% of trailing-7-day mean">
- **Contract owner + enforcement point:** <who owns it · where it blocks (merge / promotion)>

## Checks (tests — known rules at a point in time)
| Check | Type | Column(s) | Severity (block / warn) | Where it runs |
|---|---|---|---|---|
| <not-null> | not-null | <cols> | block | in-transform (dbt) |
| <unique / grain> | unique | <pk> | block | in-transform (dbt) |
| <accepted-values> | accepted-values | <enum col> | warn | in-transform (dbt) |
| <referential> | relationships | <fk → parent> | block | in-transform (dbt) |
| <value-range / distribution> | expression / expectation | <col> | warn | post-load gate |

## Monitors (unknown over time — baseline + tolerance, never a magic number)
| Monitor | Pillar | Baseline | Tolerance | Detector (threshold / statistical / ML) | Severity |
|---|---|---|---|---|---|
| <freshness> | freshness | <expected cadence> | <e.g. 2h> | threshold | block |
| <volume> | volume | <trailing-7-day mean> | <±20%> | statistical | warn |
| <schema-drift> | schema | <current schema> | <any add/drop/type-change> | threshold | block |
| <distribution> | distribution | <seasonality-aware baseline> | <±3σ> | statistical/ML | warn |

## Block-vs-warn rationale
- **Blocks:** <which checks circuit-break, and why downstream harm > pipeline-stall cost>
- **Warns:** <which checks warn-only, and why a stall would cost more than the anomaly>

## Wiring & alerting
- **Where wired:** <in-transform (dbt build) · post-load gate (GE/Soda checkpoint) · independent monitor · CI gate · orchestration step>
- **Alert routing:** <channel + who's paged per check>
- **Runbook link:** [`data-incident-runbook.md`](data-incident-runbook.md)

## SLA / SLIs
- **Freshness SLI/SLA:** <e.g. "≤ 2h behind source, 99% of business days">
- **Completeness SLI:** <row count / null rate vs baseline>
- **Validity SLI:** <% rows passing the contract rules>
- **Escalation path:** <owner → on-call → lead>

## Seams (not this team)
- **Policy / PII / access / retention:** data-governance-privacy
- **The transform/model:** analytics-engineering
- **Ingest / warehouse:** data-platform
- **Scheduling / circuit-breaker in the DAG / backfill execution:** data-orchestration

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
