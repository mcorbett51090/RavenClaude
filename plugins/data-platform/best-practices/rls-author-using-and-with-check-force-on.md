# Author Postgres RLS with FORCE on, USING + WITH CHECK, and SET LOCAL behind a pool

**Status:** Absolute rule — these four mechanics are the difference between RLS that isolates tenants and RLS that looks enabled but leaks. Security-sensitive: any change here escalates to `ravenclaude-core/security-reviewer`.

**Domain:** Multi-tenant security / RLS authoring

**Applies to:** `data-platform`

---

## Why this exists

"RLS is on" is not the same as "RLS isolates." The parent rule ([`enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md)) says *which layer* enforces; this rule is the authoring craft for the Postgres layer, because the four ways RLS silently fails to isolate are all subtle: **(1)** without `FORCE`, the table *owner* (and your ELT role connecting as owner) bypasses every policy; **(2)** a `FOR ALL` policy with `USING` but no `WITH CHECK` enforces reads but lets a write set another tenant's `tenant_id`; **(3)** `SET` instead of `SET LOCAL` leaks the tenant context across a pooled connection to the next request; **(4)** any viewer-facing role with `BYPASSRLS` skips the whole thing. Each is a one-token mistake that passes a casual review and fails a cross-tenant denial test — which is exactly why the denial test is mandatory and is the proof, not the policy text.

## How to apply

`ENABLE` + `FORCE`, both `USING` and `WITH CHECK`, `SET LOCAL` per request, index `tenant_id`, and a viewer role without `BYPASSRLS`. The hook flags a `tenant_id` `CREATE TABLE` with no `ENABLE ROW LEVEL SECURITY`.

```sql
ALTER TABLE fact_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_orders FORCE  ROW LEVEL SECURITY;      -- (1) owners/ELT bypass without FORCE

CREATE POLICY tenant_iso ON fact_orders
  FOR ALL
  USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)   -- read guard
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);  -- (2) write guard

CREATE INDEX idx_fact_orders_tenant ON fact_orders(tenant_id);            -- RLS scans all rows without it

-- Per request, behind a connection pool:
SET LOCAL app.tenant_id = '<jwt-claim-tenant_id>';      -- (3) LOCAL, not SET — pool-leak safe

-- Roles: ELT may bypass; the viewer-facing role NEVER does.
ALTER ROLE dbt_build_role  BYPASSRLS;                   -- build/truncate needs it
-- viewer_role: created WITHOUT BYPASSRLS  (4)

-- PROOF — the cross-tenant denial test (no test, no merge):
SET ROLE viewer_role; SET LOCAL app.tenant_id = 'tenant-A';
SELECT count(*) FROM fact_orders WHERE tenant_id = 'tenant-B';   -- EXPECTED: 0
```

**Do:**
- `ENABLE` **and** `FORCE` on every tenant-scoped table; `FORCE` is what stops owner/ELT bypass.
- Write both `USING` and `WITH CHECK` on `FOR ALL` policies — read guard and write guard.
- Source `tenant_id` from the signed JWT claim via `SET LOCAL`; index `tenant_id`.
- Ship the cross-boundary denial test (token for A, query B, assert zero) and run it in CI.

**Don't:**
- Omit `FORCE`, omit `WITH CHECK`, use `SET` instead of `SET LOCAL`, or grant a viewer-facing role `BYPASSRLS`.
- Derive `tenant_id` from a URL/query param.
- Merge a `tenant_id` table or an RLS change without the denial test passing — and route it through `ravenclaude-core/security-reviewer`.

## Edge cases / when the rule does NOT apply

- **Non-Postgres enforcement layers** — Cube `access_policy`, Power BI DAX roles, Snowflake row-access policies are the equivalent layer for those stacks; this rule is the Postgres-specific authoring (the hook is Postgres-only by design).
- **Single-tenant deliverable** — no tenant axis, no policy — but document the assumption so a future multi-tenant pivot doesn't inherit a silently-missing control.
- **PgBouncer pooling mode** — transaction pooling is safer than session pooling for `SET LOCAL`; verify the pool resets context per transaction.

## See also

- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) — the invariant this rule implements at the Postgres layer
- [`./issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md) — the JWT claim that feeds `SET LOCAL`
- [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — the seven footguns + per-stack defense-in-depth matrix
- [`../skills/rls-policy-authoring/SKILL.md`](../skills/rls-policy-authoring/SKILL.md) — policy templates + denial tests as skill output
- [`../templates/rls-cross-tenant-test.sql`](../templates/rls-cross-tenant-test.sql) — the denial test that must return zero rows

## Provenance

Codifies the "Postgres RLS footguns" list (1-7) and canonical pattern from `multi-tenant-rls-patterns.md` (Last reviewed 2026-05-21), CLAUDE.md house opinion #3 + §7 hook, and the `dbt-project-scaffolding` build-role/query-role separation. Postgres RLS semantics (`FORCE`, `USING`/`WITH CHECK`, `SET LOCAL`, `BYPASSRLS`) are stable Postgres behavior. Security-sensitive — escalate to `ravenclaude-core/security-reviewer`.

---

_Last reviewed: 2026-05-30 by `claude`_
