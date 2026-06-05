# Document every column description in schema.yml — not in a separate wiki

**Status:** Absolute rule
**Domain:** dbt / documentation
**Applies to:** `analytics-engineering`

---

## Why this exists

Column documentation written in a Confluence page, a Notion doc, or a README decouples from the model the moment someone renames or drops a column. The dbt `schema.yml` file travels with the model in version control, renders in `dbt docs generate`, and is the source of truth that downstream BI tools (Metabase, Looker, Power BI) can consume via metadata APIs. Documentation that lives outside the model silently diverges within weeks of the first schema change. An undocumented column in a mart is a mystery every analyst will solve differently.

## How to apply

For every model in `staging/`, `intermediate/`, and `marts/`, add a `description:` to each column in `schema.yml` before the PR is merged.

```yaml
models:
  - name: fct_orders
    description: >
      Grain: one row per order. Source: Stripe charges + QBO invoices via fct_stripe_charges
      and fct_qbo_invoices. Refreshed daily.
    columns:
      - name: order_id
        description: Surrogate key — SHA256 hash of source_system + source_order_id.
        tests:
          - not_null
          - unique

      - name: recognized_revenue_usd
        description: >
          Revenue recognized on this order in USD. Uses the invoice date as the recognition date.
          For pending/disputed orders, this is 0 until the charge clears.
        tests:
          - not_null

      - name: tenant_id
        description: UUID of the tenant who placed this order. FK to dim_tenant.tenant_id.
        tests:
          - not_null
          - relationships:
              to: ref('dim_tenant')
              field: tenant_id
```

**Do:**
- Write column descriptions at the time you author the model, not after.
- Use the `description:` as the contract: what the column means, its data type intent, its grain relation.
- Add `doc()` blocks for long shared descriptions used across multiple models.

**Don't:**
- Leave `description: ""` or omit the description entirely on any mart column.
- Write descriptions in a wiki and link to them from `schema.yml` (the link rots; the inline text doesn't).
- Use the column name as the description (`order_id: "The order ID"` is not a description).

## Edge cases / when the rule does NOT apply

Staging models may have lighter documentation (column descriptions can be deferred to intermediate/marts as long as the staging model's own `description:` covers what source it maps). But every mart column that a BI tool or downstream consumer reads must have a full description.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — owns model authoring including schema.yml
- [`./models-are-owned-and-documented.md`](./models-are-owned-and-documented.md) — the broader documentation ownership rule

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #5 ("Models are owned and documented. Every model has an owner, a description, column docs, and tests") as a standalone, mechanically-actionable rule.

---

_Last reviewed: 2026-06-05 by `claude`_
