# Declare downstream consumers with dbt exposures

**Status:** Pattern
**Domain:** dbt / lineage / impact analysis
**Applies to:** `analytics-engineering`

---

## Why this exists

Without exposures, a dbt project's lineage ends at the mart. A developer who refactors `fct_orders` has no automated way to know that three Metabase questions, one Cube cube, and a customer-facing Evidence.dev page all depend on it. Exposures make downstream consumers first-class citizens of the dbt DAG: they appear in `dbt docs`, they produce a lineage graph that includes the BI tools and dashboards, and they enable `dbt ls --select fct_orders+` to surface every downstream consumer before a breaking change is merged.

## How to apply

Add an `exposures:` block in the mart's `schema.yml` for each known downstream consumer:

```yaml
exposures:
  - name: revenue_dashboard
    type: dashboard
    maturity: high
    url: https://analytics.example.com/dashboards/12
    description: >
      Customer-facing MRR and ARR dashboard. Consumes fct_orders and dim_customer.
      Breaking changes here require customer communication.
    owner:
      name: Analytics Team
      email: analytics@example.com
    depends_on:
      - ref('fct_orders')
      - ref('dim_customer')

  - name: cube_orders_cube
    type: application
    maturity: high
    url: https://cube.example.com/
    description: >
      Cube cube definition that pre-aggregates fct_orders for the embedded dashboard.
    owner:
      name: Dashboard Builder
    depends_on:
      - ref('fct_orders')
```

Use `dbt ls --select +revenue_dashboard` to trace all upstream models; use `--select fct_orders+` to see all downstream impacts including exposures.

**Do:**
- Add an exposure for every BI tool, dashboard, notebook, or application that reads a mart model.
- Set `maturity: high` on customer-facing exposures to signal blast radius.
- Keep the `url` and `owner` current; a stale exposure is still better than no exposure.

**Don't:**
- Skip exposures because "the BI tool isn't in dbt." Exposures are documentation of the contract, not an execution graph.
- Use exposures to model internal staging-to-intermediate dependencies (those are `{{ ref(...) }}` — exposures are for external consumers).

## Edge cases / when the rule does NOT apply

- Proof-of-concept or exploratory mart models that haven't yet been wired to any downstream consumer may omit exposures — but must add them before the mart is considered production.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — authors exposures as part of mart delivery
- [`./models-are-owned-and-documented.md`](./models-are-owned-and-documented.md) — the ownership rule that exposures reinforce

## Provenance

Standard dbt exposures feature (GA in dbt Core v0.18+). Grounded in analytics-engineering CLAUDE.md §2 house opinion #5 ("Models are owned and documented") extended to downstream consumers. The impact-analysis use case is why this is a named rule rather than just a feature recommendation.

---

_Last reviewed: 2026-06-05 by `claude`_
