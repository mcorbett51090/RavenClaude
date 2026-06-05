# Observability & SRE scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) observability & SRE engagements. War stories of "the system had problem X, here was the situation, these were the constraints, we tried A/B/C, D moved the number." Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — field notes from real observability/reliability work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: observability-sre
product: <prometheus | opentelemetry | grafana | prometheus-alertmanager | generic | etc.>
product_version: <"2026.04" | "unknown" | "n/a">
scope: tenant-specific | version-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

> **Privacy:** scenarios carry **no** customer-identifying info, no real service names, no real dashboards, and no revenue/SLA figures attributable to a named org. Numbers (page counts, series counts, latency, budget minutes) are illustrative for the engagement, not measured from a named system. This mirrors the marketplace `/wrap` scrub discipline.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-alert-fatigue-slo-redesign.md`](2026-06-05-alert-fatigue-slo-redesign.md) | likely-general | alert-fatigue, slo, burn-rate, symptom-alerting, on-call, runbook | high |
| [`2026-06-05-high-cardinality-metrics-cost-blowout.md`](2026-06-05-high-cardinality-metrics-cost-blowout.md) | likely-general | cardinality, metrics-cost, tsdb, label, time-series, prometheus | high |
| [`2026-06-05-missing-instrumentation-trace-gap.md`](2026-06-05-missing-instrumentation-trace-gap.md) | likely-general | opentelemetry, distributed-tracing, context-propagation, trace-gap, instrumentation, latency | medium |
| [`2026-06-05-error-budget-burn-freeze-policy.md`](2026-06-05-error-budget-burn-freeze-policy.md) | likely-general | error-budget, slo, freeze-policy, mttr, postmortem, ship-vs-freeze | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters, different engagements) corroborate the same finding, an agent proposes promotion to a `knowledge/` decision tree or `docs/best-practices/`. As of this bank's first version, promotion is manual and the scenarios stay in place after a rule is canonicalized — the narrative remains useful context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank. The most-likely-to-benefit specialists — `observability-engineer`, `sre-reliability-engineer`, `incident-commander` — should check the bank when a situation matches.
