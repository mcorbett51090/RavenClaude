# Model dbt as staging → intermediate → marts — and never let a mart read a raw source

**Status:** Absolute rule — a mart that references `{{ source(...) }}` has bypassed the staging contract and is a layering defect, not a style choice.

**Domain:** dbt modeling / transform layer

**Applies to:** `data-platform`

---

## Why this exists

A dbt project decays the moment its dependency graph stops being a clean staging → intermediate → marts cascade. The layers each have one job: **staging** renames/casts/lightly-cleans one source table each (the only layer that touches `{{ source() }}`); **intermediate** holds reusable business logic that no dashboard reads directly; **marts** are the fact/dimension tables that *are* the BI-facing contract. When a mart reads a raw source directly, the cast/dedup/rename that staging owns either gets duplicated inconsistently across marts or skipped — and the next person can no longer trust that "fix it in staging" fixes it everywhere. The discipline is what makes the warehouse a contract instead of a pile of SQL.

## How to apply

Staging touches sources; marts touch only `ref()`. One staging model per source table. Cleaning happens in staging, never in a mart.

```sql
-- ✅ staging — the ONLY layer that references a source
-- models/staging/stripe/stg_stripe__charges.sql
select id::text as charge_id, (amount/100.0)::numeric as amount_usd, tenant_id::uuid as tenant_id
from {{ source('stripe_raw', 'charges') }}
where status = 'succeeded'

-- ✅ mart — references staging/intermediate via ref(), NEVER a source
-- models/marts/finance/fct_revenue_daily.sql
select tenant_id, date_trunc('day', charged_at) as revenue_date, sum(amount_usd) as revenue
from {{ ref('stg_stripe__charges') }}
group by 1, 2

-- ❌ mart reading a source directly — staging contract bypassed
select sum(amount/100.0) from {{ source('stripe_raw', 'charges') }}   -- DEFECT
```

**Do:**
- Reference sources **only** in staging; reference only `ref()` in intermediate and marts.
- Keep one staging model per source table; merge two tables only at the intermediate layer.
- Put every cast, rename, and dedup in staging so marts can assume clean inputs.
- Give every mart column a doc-block — the marts layer is a published contract.

**Don't:**
- Let a mart (or a dashboard query) read an `int_*` model — intermediate is private.
- Put type casts, column renames, or dedup logic in a mart.
- Run `dbt run` in CI — run `dbt build` so tests gate the marts (see [`./dbt-test-the-floor-unique-not-null-relationships.md`](./dbt-test-the-floor-unique-not-null-relationships.md)).

## Edge cases / when the rule does NOT apply

- **A genuinely source-shaped mart** (a thin pass-through dimension that is already clean at source) still goes through a one-line staging model — the indirection is cheap and preserves the invariant.
- **Case A (Evidence.dev)** — no dbt project; SQL in `.md` pages is the transform layer.
- **Client already runs Dataform / Coalesce / Matillion** — don't replatform to dbt without an explicit reason; the layering principle still holds in their tool.

## See also

- [`./etl-elt-load-then-transform-in-warehouse.md`](./etl-elt-load-then-transform-in-warehouse.md) — what lands raw before staging picks it up
- [`./dbt-test-the-floor-unique-not-null-relationships.md`](./dbt-test-the-floor-unique-not-null-relationships.md) — the test gate on the marts contract
- [`./dbt-incremental-with-unique-key-for-large-facts.md`](./dbt-incremental-with-unique-key-for-large-facts.md) — materialization for large marts
- [`../skills/dbt-project-scaffolding/SKILL.md`](../skills/dbt-project-scaffolding/SKILL.md) — the canonical layout and layer rules

## Provenance

Codifies the "Layer rules — non-negotiable" section of the `dbt-project-scaffolding` skill (staging references sources only; marts never reference sources; intermediate is private; one staging model per source table; cleaning in staging). dbt layer conventions are stable dbt-core practice.

---

_Last reviewed: 2026-05-30 by `claude`_
