# Test every FK relationship between mart models with a dbt relationships test

**Status:** Absolute rule
**Domain:** dbt / data quality
**Applies to:** `analytics-engineering`

---

## Why this exists

A foreign-key join in a mart is a claim: "every `order_id` in `fct_orders` has a matching row in `dim_customer`." Without a `relationships` test, a silently broken FK produces a left-join that inflates or deflates the metric depending on whether the null-key rows are included. Stale dim keys (a customer deleted on the source side but not yet in the dim) produce the wrong numbers silently and are invisible until a stakeholder spots the discrepancy. The `relationships` test is the cheapest catch available.

## How to apply

```yaml
models:
  - name: fct_orders
    columns:
      - name: customer_id
        description: FK to dim_customer.customer_id.
        tests:
          - not_null
          - relationships:
              to: ref('dim_customer')
              field: customer_id

      - name: tenant_id
        description: FK to dim_tenant.tenant_id.
        tests:
          - not_null
          - relationships:
              to: ref('dim_tenant')
              field: tenant_id
```

For high-volume facts where the full FK scan is too expensive, use a `warn_if` threshold:

```yaml
          - relationships:
              to: ref('dim_customer')
              field: customer_id
              config:
                severity: warn
                warn_if: ">= 10"
                error_if: ">= 100"
```

**Do:**
- Add a `relationships` test to every FK column in a mart before the model ships.
- Set severity to `error` by default; down-grade to `warn` only with a documented reason.
- Run `dbt test --select fct_orders` in CI before merging any mart change.

**Don't:**
- Skip relationship tests on "obvious" FKs that "will always match."
- Use a `left join` on an untested FK and assume nulls are acceptable without a documented decision.
- Add the test after go-live — by then the mart is already serving broken joins.

## Edge cases / when the rule does NOT apply

- Late-arriving dimension rows (e.g., a CRM contact that is created after the first event is logged) may legitimately produce null FKs. In this case, use `warn` severity and document the expected null-key rate and the business reason.

## See also

- [`../agents/data-quality-testing-engineer.md`](../agents/data-quality-testing-engineer.md) — owns the test taxonomy and severity tiers
- [`./test-data-like-code.md`](./test-data-like-code.md) — the parent rule this enforces

## Provenance

Codifies analytics-engineering CLAUDE.md §2 house opinion #3 ("Test the data like code") at the FK-relationship test level — the specific test type that guards mart join correctness.

---

_Last reviewed: 2026-06-05 by `claude`_
