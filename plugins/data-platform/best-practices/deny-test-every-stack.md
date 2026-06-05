# Ship a cross-boundary denial test for every tenant-isolation stack

**Status:** Absolute rule
**Domain:** Multi-tenant security / testing
**Applies to:** `data-platform`

---

## Why this exists

A tenant-isolation control is only as good as the test that proves it fires. Postgres RLS enabled with `ENABLE ROW LEVEL SECURITY` but no `FORCE ROW LEVEL SECURITY` leaks to the table owner. A Cube `securityContext` scope rule that passes a literal `null` at startup lets every query through. A missing `access_policy` on a Power BI dataset leaves row-level security as opt-in. In each case the system *looks* locked and *is* open. The only way to know the control fires is to attempt a cross-boundary read and assert it returns zero rows. No test, no merge.

## How to apply

Every stack ships one cross-boundary denial test appropriate to its enforcement layer:

**Postgres RLS** — run as a non-owner role with a valid session token for Tenant A, then query for Tenant B rows. Assert `COUNT(*) = 0`.

```sql
-- rls_cross_tenant_denial_test.sql
-- Must return exactly zero rows.
SET LOCAL role = 'tenant_a_service_role';
SET LOCAL app.current_tenant = 'tenant-a-uuid';

SELECT COUNT(*) AS cross_tenant_leak
FROM orders
WHERE tenant_id = 'tenant-b-uuid';
-- Expected: 0
```

**Cube semantic layer** — run as a user whose `securityContext.tenant_id` is set to Tenant A's ID; call a Cube endpoint that would return Tenant B data if the scope rule is absent. Assert the response is empty.

**Power BI App-Owns-Data** — generate an embed token with EffectiveIdentity set to a Tenant A user, then attempt to pull a report visual filtered for Tenant B. Assert the visual returns no data.

**dbt + warehouse layer** — add a `singular` dbt test in `tests/cross_tenant_leak.sql` that asserts zero rows using a controlled test fixture:

```sql
-- tests/cross_tenant_leak.sql
-- dbt singular test: fails if any row is returned
SELECT *
FROM {{ ref('fct_orders') }}
WHERE tenant_id != (
    SELECT tenant_id FROM test_fixtures.session_tenant LIMIT 1
)
AND session_set_to = (
    SELECT tenant_id FROM test_fixtures.session_tenant LIMIT 1
)
```

Add to CI: `dbt build --select tag:denial_test` must pass in the same workflow that runs migrations.

**Do:**
- Write the denial test *before* enabling the isolation control and treat a passing test before the control is on as the red-phase baseline.
- Run it in CI, not just in local dev.
- Tag it (`tag: denial_test`) so it can be selected in isolation and run on every PR that touches the tenant-isolation control.
- Keep it in the repo alongside the migration/policy it tests.

**Don't:**
- Skip the test because the RLS policy "looks correct" — the policy's USING clause may be syntactically valid but semantically wrong.
- Substitute a visual spot-check in the dashboard for a programmatic assertion.
- Mark the test as `warn` severity — it must be `error` so it blocks a build.

## Edge cases / when the rule does NOT apply

Single-tenant deliverables have no tenant axis and thus no cross-boundary isolation to test. Document the single-tenant assumption explicitly so a future multi-tenant pivot knows to add this gate. No other exceptions — every multi-tenant stack ships the test.

## See also

- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — generates the RLS policies and owns the SQL denial test
- [`./rls-author-using-and-with-check-force-on.md`](./rls-author-using-and-with-check-force-on.md) — the companion rule on how to write the RLS policy this test validates
- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) — the foundational invariant this test enforces

## Provenance

Codifies `CLAUDE.md` §3 #3 ("Every stack ships a cross-boundary denial test appropriate to its enforcement layer. No test, no merge.") and §4 ("A dashboard built on a semantic layer where the cross-boundary denial test was skipped"). The SQL template mirrors `templates/rls-cross-tenant-test.sql`.

---

_Last reviewed: 2026-06-05 by `claude`_
