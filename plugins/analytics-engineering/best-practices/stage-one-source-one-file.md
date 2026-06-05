# One staging model per source table — no cross-source logic in staging

**Status:** Absolute rule
**Domain:** dbt / layering
**Applies to:** `analytics-engineering`

---

## Why this exists

A staging model that joins two source tables is an intermediate model wearing staging clothes. When it is categorized as staging, downstream developers assume it maps one source — and they will be surprised by the hidden join. More critically, a staging model that joins Stripe charges to QBO invoices builds a coupling between two source schemas: a type change in either source breaks a model that is supposed to be a thin cleaning layer. Staging models are the single-source contract; composition happens in intermediate.

## How to apply

Naming convention and directory structure enforce the rule:

```
models/
  staging/
    stripe/
      stg_stripe__charges.sql        # maps raw.stripe.charges ONLY
      stg_stripe__customers.sql      # maps raw.stripe.customers ONLY
    quickbooks/
      stg_quickbooks__invoices.sql   # maps raw.qbo.invoices ONLY
  intermediate/
    int_orders__stripe_qbo_joined.sql  # joins stg_stripe__charges + stg_quickbooks__invoices
  marts/
    fct_orders.sql                   # refs intermediate models
```

**In `stg_stripe__charges.sql`:**
```sql
-- Only references {{ source('stripe', 'charges') }}
-- Only renames, casts, or lightly filters this one table
select
    id as charge_id,
    amount / 100.0 as amount_usd,
    created as created_at
from {{ source('stripe', 'charges') }}
```

**Do:**
- Give every staging model exactly one `{{ source(...) }}` reference.
- Use the naming convention `stg_<source>__<table>.sql` to make the one-to-one relationship explicit.
- Subdirectory-organize staging by source system so the directory structure reinforces the rule.

**Don't:**
- Join two sources in a staging model "because the business logic is simple."
- Alias a source table and a staging model with the same name, creating ambiguity about what is already cleaned.

## Edge cases / when the rule does NOT apply

- Staging models may join the same source table to itself (a self-join) for recursive hierarchies. This is still a single-source model.
- A staging model may reference a `{{ ref(...) }}` seed file (a dbt seed is not a source, it's a project artifact).

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — owns the staging layer architecture
- [`./never-ref-a-source-outside-staging.md`](./never-ref-a-source-outside-staging.md) — the companion rule that prevents source refs from leaking into later layers

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #2 ("Staging cleans and renames one source") as a standalone file-structure enforcement rule. This is the Fishtown Analytics / dbt Labs canonical staging discipline.

---

_Last reviewed: 2026-06-05 by `claude`_
