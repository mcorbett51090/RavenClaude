# Never reference a source directly outside staging models

**Status:** Absolute rule
**Domain:** dbt / layering
**Applies to:** `analytics-engineering`

---

## Why this exists

`{{ source('stripe', 'charges') }}` referenced in an intermediate or mart model bypasses the staging contract entirely. The staging layer exists to normalize field names, cast types, and add `_at` timestamp columns — once. If two models independently reference the same raw source, a source schema change (a renamed column, a type cast) must be fixed in two places. More insidiously, an intermediate that bypasses staging gets the raw, un-normalized names — `created` instead of `created_at`, `amt` instead of `amount_usd` — and every downstream query inherits that inconsistency.

## How to apply

```sql
-- staging/stg_stripe__charges.sql
-- CORRECT: staging is the ONLY place that references the source
select
    id                          as charge_id,
    amount / 100.0              as amount_usd,     -- cents → dollars, once
    created                     as created_at,
    customer                    as stripe_customer_id,
    status                      as charge_status
from {{ source('stripe', 'charges') }}

-- intermediate/int_orders__enriched.sql
-- CORRECT: references the staging model, not the source
select
    c.charge_id,
    c.amount_usd,
    c.created_at,
    q.invoice_id
from {{ ref('stg_stripe__charges') }} c
left join {{ ref('stg_quickbooks__invoices') }} q
    on c.stripe_customer_id = q.customer_id
```

**CI lint (add to `dbt_project.yml` or a custom test):**
```yaml
# Enforce: only staging models may reference sources
models:
  intermediate:
    +required_tests: []  # no source refs should appear
```

Or add a SQLFluff rule (or a simple grep in CI): `grep -rn "source(" models/intermediate models/marts` → fail if any match.

**Do:**
- Put every `{{ source(...) }}` call in `staging/` only.
- Keep staging models thin: rename, cast, light filter — nothing more.
- Enforce with a CI grep or a custom dbt test on intermediate/mart directories.

**Don't:**
- Use `{{ source(...) }}` in intermediate or mart models, even "just this once."
- Mix staging and intermediate logic in one model to save a file.

## Edge cases / when the rule does NOT apply

- The `snapshots/` directory uses `{{ source(...) }}` directly by design (snapshot captures the raw table state). This is correct and not a violation.
- A one-shot migration script (not a dbt model) can reference a source directly; this rule governs the dbt DAG, not ad-hoc SQL.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — owns the staging layer contract
- [`./transform-in-layers.md`](./transform-in-layers.md) — the parent layering rule this enforces

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #2 ("Transform in layers: staging -> intermediate -> marts") at the mechanical enforcement level — specifically the invariant that `{{ source(...) }}` appears only in `staging/`.

---

_Last reviewed: 2026-06-05 by `claude`_
