# Performance Engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real performance-engineering engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real performance work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: performance-engineering
product: <k6 | gatling | locust | jmeter | async-profiler | pprof | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-coordinated-omission-hid-the-tail.md`](2026-06-08-coordinated-omission-hid-the-tail.md) | load-test, coordinated-omission, open-vs-closed, percentiles | `avoid-coordinated-omission`, `open-vs-closed-is-a-choice`, `percentiles-not-averages` |
| [`2026-06-08-optimized-the-wrong-thing.md`](2026-06-08-optimized-the-wrong-thing.md) | profiling, flame-graph, use-red, off-cpu, bottleneck | `profile-before-you-optimize`, `headroom-is-computed-not-vibed` |
| [`2026-06-08-the-leak-only-showed-after-six-hours.md`](2026-06-08-the-leak-only-showed-after-six-hours.md) | soak-test, memory-leak, connection-pool, test-the-edges, regression | `test-the-edges-not-just-the-steady-state`, `regression-needs-a-baseline` |
| [`2026-06-08-the-spike-broke-what-steady-load-didnt.md`](2026-06-08-the-spike-broke-what-steady-load-didnt.md) | spike-test, elasticity, autoscaling, recovery, test-the-edges | `test-the-edges-not-just-the-steady-state`, `prove-the-bottleneck-hand-off-the-fix` |
| [`2026-06-08-planned-to-the-knee-with-no-headroom.md`](2026-06-08-planned-to-the-knee-with-no-headroom.md) | capacity, littles-law, headroom, failover, saturation-point | `headroom-is-computed-not-vibed`, `prove-the-bottleneck-hand-off-the-fix` |
