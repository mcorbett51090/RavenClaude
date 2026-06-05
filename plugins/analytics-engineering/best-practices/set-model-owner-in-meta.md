# Set a named model owner in meta for every mart

**Status:** Absolute rule
**Domain:** dbt / ownership / governance
**Applies to:** `analytics-engineering`

---

## Why this exists

An undocumented mart is a mystery the business will misuse. An unowned mart is a mystery no one will fix. When a mart produces a wrong number, "who owns this?" should have a one-command answer: `dbt ls --select fct_orders --output json | jq '.meta.owner'`. Without a `meta.owner` field, the investigation starts with a git blame that may point to a consultant who has since rolled off the engagement. The `meta` block also propagates to `dbt docs` and downstream catalog tools (Datahub, Atlan, OpenMetadata) where stakeholders can self-serve the ownership question.

## How to apply

```yaml
models:
  - name: fct_orders
    description: Grain: one row per order. Source: fct_stripe_charges + fct_qbo_invoices.
    meta:
      owner: analytics-team
      owner_email: analytics@example.com
      domain: revenue
      pii: false
      refresh_cadence: daily
    columns:
      - name: order_id
        description: Surrogate key.
        tests:
          - not_null
          - unique
```

At minimum, set `owner` (team or person). Use the same `meta` shape across the project so catalog integrations can parse it consistently.

**Optional: enforce at CI with a custom dbt test:**

```python
# tests/generic/model_has_owner.sql
{% test model_has_owner(model, column_name) %}
  select 1 where false  -- dummy; enforce via check-manifest.py instead
{% endtest %}
```

Or add a `check-manifest.py` step to CI that reads `dbt ls --output json` and fails the build if any mart is missing `meta.owner`.

**Do:**
- Set `meta.owner` on every model in `marts/` before the PR merges.
- Use a team identifier, not a personal name, so ownership survives personnel changes.
- Add `domain:` to group marts by subject area for catalog consumers.

**Don't:**
- Leave `meta: {}` or omit `meta` on mart models.
- Use "TBD" or "unknown" as the owner — a placeholder is worse than an honest "analytics-team" catch-all.

## Edge cases / when the rule does NOT apply

- Staging and intermediate models may use lighter meta (just a domain tag); the full ownership requirement applies to marts and any model directly consumed by a BI tool or exposure.

## See also

- [`../agents/analytics-engineer.md`](../agents/analytics-engineer.md) — authors the meta block at model-creation time
- [`./document-col-descriptions-in-schema-yml.md`](./document-col-descriptions-in-schema-yml.md) — the companion column-documentation rule

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #5 ("Models are owned and documented. Every model has an owner") as a mechanically-checkable enforcement point using dbt's `meta` block.

---

_Last reviewed: 2026-06-05 by `claude`_
