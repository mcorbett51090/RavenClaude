# Enforce model contracts on boundaries — break loudly, never silently

**Status:** Absolute rule
**Domain:** dbt / contracts / data quality
**Applies to:** `analytics-engineering`

---

## Why this exists

A dbt model contract (`contract: enforced: true`) declares that the model's column names and data types are a published API. Without enforcement, a developer who renames `amount_usd` to `revenue_usd` in a mart will rebuild successfully — but every Cube cube, Metabase question, or downstream staging model that referenced the old column name will silently break or return null. dbt model contracts cause the build to fail at the mart boundary if a column name or type is changed without a corresponding contract update, making the breakage explicit rather than invisible.

## How to apply

```yaml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    description: Published mart API — column renames and type changes are breaking changes.
    columns:
      - name: order_id
        data_type: varchar
        constraints:
          - type: not_null
      - name: recognized_revenue_usd
        data_type: numeric
        constraints:
          - type: not_null
      - name: tenant_id
        data_type: uuid
        constraints:
          - type: not_null
```

With `enforced: true`, a `dbt build` will fail if the actual mart SQL produces a column not listed, a type mismatch, or missing a listed column.

**Breaking change process:**
1. Bump the mart's semantic version in `meta.version`.
2. Add a migration note in the model's description.
3. Update all downstream `{{ ref('fct_orders') }}` consumers in the same PR.
4. Run `dbt build` in CI to confirm the contract is satisfied.

**Do:**
- Enforce contracts on every mart that a BI tool, Cube cube, or external consumer reads.
- Treat a contract violation as a breaking change requiring a version bump and migration note.
- Add contract enforcement before the first external consumer is connected.

**Don't:**
- Turn off contract enforcement to "make a quick rename easier."
- Add a contract after breaking changes have already shipped silently.

## Edge cases / when the rule does NOT apply

- Staging and intermediate models are internal — contracts are optional there. The boundary that needs the contract is between the transform layer and the consuming BI/semantic layer.
- A one-off mart for a single analysis session (not a recurring dashboard source) may omit contract enforcement.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — adds contract enforcement at mart authoring time
- [`./contract-the-consumer-boundary.md`](./contract-the-consumer-boundary.md) — the broader boundary-contract rule this specializes

## Provenance

Codifies the dbt model contracts feature (GA in dbt Core v1.5+) as a named rule. Grounded in analytics-engineering CLAUDE.md §2 house opinion #5 ("Models are owned and documented") — a contract is the machine-enforced form of that ownership.

---

_Last reviewed: 2026-06-05 by `claude`_
