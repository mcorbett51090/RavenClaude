# Define each metric once in the semantic layer — never re-derive it per dashboard

**Status:** Pattern — strong default for Case C (productized SaaS) and any multi-dashboard engagement; deviate only when there is exactly one dashboard reading one mart and no reuse in sight.

**Domain:** Semantic modeling / metric governance

**Applies to:** `data-platform`

---

## Why this exists

When "active customer" or "recognized revenue" is defined as ad-hoc SQL inside each dashboard widget, the definitions drift: one chart counts trials as active, another doesn't, and the same KPI shows two numbers on two pages. The fix is a **semantic layer** (Cube for Case C, dbt MetricFlow / Power BI model for others) that defines each measure and dimension **once**, and every dashboard queries *that* definition — so "revenue" means one thing everywhere, with one query plan, one cache, and one access-control surface. This is also the non-negotiable for customer-facing scale: a productized dashboard shipping raw SQL to the browser has no caching, no query governance, and no place to enforce tenant scope (the `securityContext` lives in the semantic layer). The rule composes with isolation — the semantic layer is simultaneously the single source of metric truth *and* the closest-to-data enforcement point the viewer's token can't influence.

## How to apply

Define the measure + dimension once in the cube; reference it from every widget. Never let a customer-facing endpoint ship raw SQL.

```yaml
# cubes/orders.yml — revenue is defined ONCE, here.
cubes:
  - name: orders
    sql_table: analytics.fct_revenue_daily
    measures:
      - name: revenue            # the canonical definition; every dashboard uses this
        sql: revenue
        type: sum
      - name: active_customers
        sql: customer_id
        type: count_distinct
        filters: [{ sql: "{CUBE}.status = 'active'" }]   # the definition of "active" lives here
    dimensions:
      - name: revenue_date
        sql: revenue_date
        type: time
      - name: tenant_id
        sql: tenant_id
        type: string
    access_policy:                # single metric truth AND the isolation point
      - role: viewer
        row_level:
          filters: [{ member: orders.tenant_id, operator: equals, values: ["{ securityContext.tenant_id }"] }]
```

**Do:**
- Define every measure and dimension once in the semantic layer; dashboards reference, never re-derive.
- Put pre-aggregations in the semantic layer so customer-facing endpoints hit a rollup, not raw SQL.
- Co-locate tenant scope (`securityContext` / `access_policy`) with the metric definitions — one surface for truth and isolation.
- Treat the dbt marts as the stable contract the semantic layer reads (staging→marts→semantic, never semantic→raw).

**Don't:**
- Ship raw SQL queries to a customer-facing dashboard endpoint — the semantic layer owns the query plan, caching, and access control.
- Redefine a KPI inline in a widget; if two widgets disagree on a number, a definition leaked out of the layer.
- Build a Cube `cubes/` directory without an `access_policy` — even a stub seam, never absent.

## Edge cases / when the rule does NOT apply

- **Case A (Evidence.dev portfolio)** — single-author, version-controlled SQL-in-markdown *is* the single source of truth; a separate semantic layer is overhead that doesn't pay back.
- **Case B with one dashboard on one mart** — a Metabase model or the mart itself can carry the definition; a full Cube layer is premature until reuse appears.
- **Power BI engagements** — the semantic layer is the Power BI model (measures in DAX); the principle holds, the tool differs — coordinate with `power-platform/power-bi-engineer`.

## See also

- [`./dbt-stage-then-mart-never-skip-the-layer.md`](./dbt-stage-then-mart-never-skip-the-layer.md) — the marts contract the semantic layer reads
- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) — the semantic layer doubles as the isolation point
- [`./warehouse-partition-and-cluster-for-cost.md`](./warehouse-partition-and-cluster-for-cost.md) — pre-aggregations reduce scan further
- [`../skills/cube-schema-scaffolding/SKILL.md`](../skills/cube-schema-scaffolding/SKILL.md) — measure/dimension/pre-agg patterns with `securityContext` baked in
- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — owns the semantic-layer scaffold

## Provenance

Distilled from CLAUDE.md house opinion #5 ("Pre-aggregate in the semantic layer; Cube owns the query plan, caching, and access control") + #7 (provenance on every claim), the `cube-schema-scaffolding` skill, and `embedded-analytics-landscape-2026.md` ("Cube is the strongest non-BI building block … semantic layer + caching + API layer"). `[verify-at-build]` Cube YAML `access_policy` / `row_level` key names — Cube's policy syntax has evolved; confirm against current Cube data-modeling docs.

---

_Last reviewed: 2026-05-30 by `claude`_
