# Never route raw warehouse SQL directly to a viewer-facing endpoint

**Status:** Absolute rule
**Domain:** Semantic layer / security
**Applies to:** `data-platform`

---

## Why this exists

A dashboard widget that fires an ad-hoc SQL query directly against the warehouse under viewer credentials bypasses every access control, query governance, and cost protection that the semantic layer provides. The viewer can inspect the query in browser devtools; if the connection uses a broad read role, the viewer may be able to alter the query to read other tenants' data. Even with RLS in place, the semantic layer is the designed enforcement point for query plans, pre-aggregations, and tenant-scoped scope rules. Bypassing it is a layering defect, not a performance shortcut.

## How to apply

The data path from warehouse to viewer must always go through the semantic layer:

```
Warehouse (Postgres / DuckDB / Snowflake)
  └─ Semantic layer (Cube / dbt Semantic Layer / Power BI / Metabase API)
       └─ Dashboard (Evidence / Superset / React + Tremor + Recharts)
            └─ Viewer
```

**Prohibited patterns:**
- A React component that calls `supabase.from('fct_orders').select('*')` under a viewer JWT (viewer can read the raw table)
- A Superset dataset that points directly at the raw `public.raw_stripe_charges` table instead of a mart
- A Cube cube that exposes `sql_table: raw.hubspot_contacts` with no `access_policy`

**Required pattern:**
- Every viewer-facing query goes through a named Cube cube (or equivalent) with a `securityContext`-enforced scope rule
- Direct database credentials are never embedded in front-end code; they live only in the semantic layer's server-side config

**Do:**
- Validate at PR review that no front-end component contains a raw `SELECT` or a direct DB client initialization.
- Add a CI lint rule (grep for `supabase.from`, `pg.query`, `mysql.query` in frontend bundles) to catch raw DB calls.
- Treat any direct-to-warehouse read path as a severity-1 layering defect requiring immediate rework.

**Don't:**
- Use the Supabase `anon` key in the front end to query mart tables directly, even with RLS in place.
- Add "temporary" raw SQL endpoints "just for development" — temporary becomes permanent.

## Edge cases / when the rule does NOT apply

- Server-side rendering (SSR) that runs a warehoused query on behalf of the viewer — in a trusted server context — is acceptable when the server applies the same tenant scope rules the semantic layer would. Document the substitution and route through the security reviewer.

## See also

- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — owns the data path from semantic layer to widget
- [`./cube-preaggregate-before-viewer.md`](./cube-preaggregate-before-viewer.md) — the pre-aggregation rule that semantic-layer routing enables

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #5 ("Pre-aggregate in the semantic layer. Don't ship raw SQL queries to a customer-facing dashboard endpoint") and §4 anti-patterns ("Dashboards that hard-code tenant IDs anywhere in the rendering layer").

---

_Last reviewed: 2026-06-05 by `claude`_
