# Write the Success Metric Before Writing the Spec

**Status:** Absolute rule
**Domain:** Product discovery / PRD
**Applies to:** `product-management`

---

## Why this exists

A spec written before the success metric is defined is a solution looking for a problem to solve. Without a pre-committed outcome metric, the team defaults to measuring completion ("shipped on time") rather than value ("retention improved"). The failure mode is subtle: teams ship features diligently, the metric question is asked post-launch, and the only honest answer is "we didn't measure it." Pre-committing to the metric before the spec is written forces the product team to answer the outcome question while there is still time to adjust the solution shape. It also makes post-launch evaluation unambiguous — the question of "did it work?" has a pre-agreed answer, not a negotiated one.

## How to apply

Make the success metric the first section of every PRD, initiative brief, or discovery doc — before the problem statement, before the solution, before the acceptance criteria.

```
PRD / Initiative Brief — Opening Section (in order)
──────────────────────────────────────────────────────
1. SUCCESS METRIC (first)
   Target metric: <exact metric name, e.g., "7-day retention rate for new users">
   Baseline: <current value, e.g., "42% as of 2026-05-01 (last 4-week average)">
   Target: <e.g., "48% — a 6 ppt improvement — within 8 weeks of launch">
   Measurement method: <where the data comes from; who reads it; how often>
   Guardrail metric: <what we're NOT allowed to break, e.g., "activation rate stays ≥ 35%">

2. PROBLEM STATEMENT (second, shaped by the metric gap)
   ...

3. SOLUTION HYPOTHESIS (third)
   ...
```

**Do:**
- Express the success metric as a rate or cohort measure, not a cumulative total (totals always go up).
- Name a guardrail metric alongside the target metric — success on the target at the cost of a different metric is not a win.
- Get explicit sign-off on the success metric from the team, the engineering lead, and the data analyst before any design work begins.
- Write "metric to move, not feature to ship" in the initiative objective line.

**Don't:**
- Accept "increase engagement" as a success metric — it is not measurable; name the specific engagement signal.
- Allow the metric to be written after the design is complete; the design will unconsciously be shaped to make the metric look achievable.
- Use a metric that can only be read 6+ months after launch as the primary success indicator; break it into a leading-indicator proxy if the true metric is long-lag.

## Edge cases / when the rule does NOT apply

- **Compliance-driven work** (e.g., GDPR data-deletion pipeline, accessibility requirement) — the success metric is "compliant by date X"; the rule applies but the metric is a binary compliance gate, not a business metric.
- **Explorations and spikes** (technical investigations without a user-visible outcome) — a learning goal substitutes for a business metric; the commitment is to a specific question to be answered, not a metric to be moved.

## See also

- [`../agents/product-metrics-analyst.md`](../agents/product-metrics-analyst.md) — owns metric definition, input-metric selection, and the pre-committed measurement plan.
- [`./north-star-with-input-metrics.md`](./north-star-with-input-metrics.md) — the success metric in the PRD should be one of the input metrics in the North Star hierarchy; if it isn't, ask why.

## Provenance

Codifies the product-metrics-analyst's pre-committed success metric discipline from the product-management plugin's CLAUDE.md §2 #4 (outcomes over outputs) and §2 #5 (North Star with input metrics). The "metric before spec" discipline reflects Teresa Torres' continuous discovery framework and standard outcome-based product development practice.

---

_Last reviewed: 2026-06-05 by `claude`_
