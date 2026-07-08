# data-quality-observability

> The **trust layer** for Claude Code — the team that answers *"is this data correct, fresh, complete, and can we rely on it?"* and builds the contracts, tests, and monitors that make the answer defensible. Two agents: the **data-quality-architect** (chooses the DQ approach + tooling) and the **data-quality-engineer** (implements the checks/monitors and runs data-incident response).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "dbt tests, Great Expectations, Soda, or a managed observability platform?" | A decision-tree-driven approach + tool choice + where the checks run + the conditions that would flip it |
| "Write a data contract for this dataset." | A producer-boundary contract: schema, semantics, freshness/volume expectations, ownership — enforced, not aspirational |
| "What tests should this table have?" | A concrete suite (not-null / unique / accepted-values / referential / distribution) scoped by the contract and the consumers |
| "Alert us before a stakeholder notices bad data." | Freshness + volume + schema-drift + distribution monitors with baselines, tolerances, owners, and block-vs-warn per check |
| "The numbers are wrong this morning — what happened?" | A data-incident runbook run: triage → severity → quarantine/circuit-breaker → root-cause to the *change* → backfill correction |
| "Set data-quality SLAs we can actually hold." | SLAs/SLIs per dataset (freshness, completeness, validity) with owners and an escalation path |

**Two rules it never breaks:** *trust is the product* (a check nobody owns is noise, and a dashboard nobody trusts is worthless), and *a test asserts a known rule, a monitor watches for the unknown — you ship both.*

## What's inside

- **2 agents** — `data-quality-architect` (chooses contracts-vs-tests-vs-monitors mix, tool, and where checks run) and `data-quality-engineer` (implements the checks/monitors, wires CI/orchestration + alerting, and runs data-incident response).
- **3 skills** — `choose-data-quality-approach`, `design-data-contracts-and-tests`, `set-up-data-observability-monitors`.
- **2 knowledge files** — a Mermaid data-quality tooling decision tree (+ trade-off table + "where do checks run" sub-choice) and a 2026 data-observability-patterns reference (5 pillars, test-vs-monitor, circuit-breaker/quarantine, anomaly detection, SLAs/SLIs, incident severity, tooling map).
- **2 templates** — a data-quality check spec and a data-incident runbook.

## Where it sits in the data stack

```
data-platform           →  ingest / connectors / warehouse / BI   ("get the data in & served")
analytics-engineering   →  dbt transforms                         ("model the data")
data-orchestration      →  RUN & SCHEDULE the pipelines           ("what runs it, when, safely")
data-governance-privacy →  policy / PII / lineage governance      ("are we ALLOWED to, and by whom")
data-quality-observability (HERE)  →  is it CORRECT / FRESH / COMPLETE / TRUSTED  ("can we rely on the number")
```

This plugin is the **trust/quality layer** *over* the others: it contracts the datasets `data-platform` lands, tests the models `analytics-engineering` builds, monitors the runs `data-orchestration` schedules, and stays clear of the *policy* questions (who may access, PII handling, retention) that belong to `data-governance-privacy`.

## Tooling stance

Concept-first (contracts, tests-vs-monitors, the 5 observability pillars, block-vs-warn, baselines/tolerances, SLAs/SLIs, incident severity), fluent across **dbt tests + dbt-expectations**, **Great Expectations**, **Soda Core / Soda Cloud**, and **Elementary**, with the managed observability platforms (**Monte Carlo, Bigeye, Metaplane**) and **warehouse-native checks** as options. Platform feature sets and pricing carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install data-quality-observability@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
