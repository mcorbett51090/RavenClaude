# Define metrics as code in the semantic layer — never derive them inside dashboard SQL

**Status:** Absolute rule
**Domain:** Semantic layer / metrics governance
**Applies to:** `analytics-engineering`

---

## Why this exists

When "Monthly Recurring Revenue" is defined as a SQL expression inside a Metabase question, a Superset chart query, and a Cube cube — each slightly differently — it is not one metric. It is three metrics that will diverge the moment any one of them is touched. The semantic/metrics layer (dbt Semantic Layer / MetricFlow, or Cube measures) exists specifically to own this definition once. Once-defined metrics are versioned, tested, and referenceable across every BI surface. A metric defined inside a dashboard SQL block has no tests, no owner, no version, and no canonical reference.

## How to apply

```yaml
# dbt Semantic Layer / MetricFlow — models/metrics/revenue.yml
semantic_models:
  - name: orders
    model: ref('fct_orders')
    entities:
      - name: order_id
        type: primary
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
    measures:
      - name: recognized_revenue
        agg: sum
        expr: recognized_revenue_usd

metrics:
  - name: monthly_recurring_revenue
    label: Monthly Recurring Revenue (MRR)
    type: simple
    type_params:
      measure: recognized_revenue
    filter: |
      {{ Dimension('order__order_type') }} = 'subscription'
```

Every downstream BI tool queries `monthly_recurring_revenue` via the MetricFlow API or Cube SDK — it does not re-implement the filter.

**Do:**
- Enumerate every business KPI (revenue, active user, churn, NPS) in the semantic layer before a dashboard is built.
- Treat a dashboard SQL override of a governed metric as a layering defect — route it back to the semantic layer.
- Add `not_null` and `positive_values` tests to every metric's underlying measure in dbt.

**Don't:**
- Implement metric logic (date filtering, subscription type filter) directly in dashboard tool SQL.
- Let two BI tools derive the "same" metric differently "because the semantic layer is complex."
- Skip the semantic layer for "simple" metrics — simplicity is not a justification; governance is.

## Edge cases / when the rule does NOT apply

- One-off exploratory analysis by a data analyst is exempt — a notebook query is not a governed metric. The rule applies to any metric intended for a recurring dashboard or a cross-team-cited KPI.

## See also

- [`../agents/semantic-layer-engineer.md`](../agents/semantic-layer-engineer.md) — owns the metrics-as-code definition
- [`./one-definition-per-metric.md`](./one-definition-per-metric.md) — the parent rule this enforces

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #1 ("One definition per metric, defined once") at the mechanical level — the enforcement mechanism is metrics-as-code in the semantic layer, not just policy.

---

_Last reviewed: 2026-06-05 by `claude`_
