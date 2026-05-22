---
name: multi-tenant-migration
description: Migrate a single-tenant database / dashboard stack to multi-tenant — `tenant_id` column propagation + backfill, RLS / semantic-layer scope rules introduced post-hoc, JWT-claim shape migration, embed-token cutover plan with parallel + backout window, and the mandatory cross-boundary denial test before flipping the switch. Reach for this skill when an engagement shifts from one-client deliverable to productized SaaS. Used by `database-setup-guide` (primary) + `dashboard-builder`.
---

# Skill: multi-tenant-migration

> **Invoked by:** `database-setup-guide` (primary — owns the schema migration) + `dashboard-builder` (owns the embed-token + semantic-layer side of the cutover). Mandatory `ravenclaude-core/security-reviewer` review before cutover.
>
> **When to invoke:** an engagement shifts from one-client deliverable to productized SaaS; a single-tenant proof-of-value moves to multi-customer; a Case B (per-client deliverable) productizes into Case C (productized SaaS) per [`./stack-selection.md`](stack-selection.md); inheriting a single-tenant codebase and the next client lands next month.
>
> **Output:** schema with `tenant_id` propagated, backfilled, indexed, NOT NULL constrained, RLS or semantic-layer scope rules in place, JWT issuer updated with `tenant_id` claim, parallel-mode → cutover → backout-window plan executed, denial test passing in CI.

## What "multi-tenant" means in this skill

The single-tenant → multi-tenant migration touches **five surfaces**, in this order:

1. **Database schema** — `tenant_id` column on every fact / dimension table
2. **Backfill** — populate the column for existing rows
3. **Enforcement layer** — RLS (Postgres) or semantic-layer scope (Cube / Power BI)
4. **JWT-claim shape** — embed token now carries `tenant_id`
5. **Embed-token cutover** — parallel mode → cutover → backout window

**Order is non-negotiable.** Adding the JWT claim before the DB enforces it is silently insecure. Adding RLS before the column exists fails the migration. Backfill without the column being NOT NULL leaves a permanent attack surface.

## Pre-migration assessment (run before any DDL)

```
[Q1] How many tenants exist *today*?
  - 1 → easy case (column added; one value to backfill)
  - 2-3 (mid-migration discovered) → moderate (per-tenant disjoint backfill)
  - "we mixed tenant data" → STOP. This is a data-separation incident, not a migration. Escalate to security-reviewer.

[Q2] Is there a viewer-facing read path today?
  - Yes → cutover requires parallel-mode + backout window (this skill)
  - No (back-office only) → simpler; deploy + enforce in one shot

[Q3] Which enforcement layer fits the stack? (see closeness-to-data invariant — [`./rls-policy-authoring.md`](rls-policy-authoring.md))
  - Raw Postgres + Metabase/Superset → Postgres RLS
  - Cube / dbt-semantic → semantic-layer scope rule
  - Power BI Embedded → DAX role
  - Fabric → OneSecurity row-level
  - Snowflake / Databricks → row-access policy

[Q4] Where does the tenant identity come from at runtime?
  - JWT claim issued by the host app (preferred — see [`./jwt-embed-issuance.md`](jwt-embed-issuance.md))
  - Subdomain (e.g., tenant.app.example) — needs JWT to ALSO carry it (subdomain is a UX hint, not security)
  - URL path parameter — same caveat as subdomain
```

## Step 1 — `tenant_id` column propagation

### Naming + type convention (use exactly this)

- **Column name:** `tenant_id` (not `org_id`, `customer_id`, `account_id` — those collide with tenant-owned entities)
- **Type:** `uuid` (preferred) or `text` (if the host app's tenant identity is already a string like `acme-corp`)
- **Nullable:** `NULL` during migration; flip to `NOT NULL` after backfill (see Step 2)
- **Default:** none — never default to a value, it hides missing-context bugs
- **Indexed:** yes, on every fact table; composite with other hot filters where useful

### Migration DDL (Postgres example)

```sql
-- A. Add the column nullable (so existing rows don't break)
ALTER TABLE fact_orders ADD COLUMN tenant_id uuid;
ALTER TABLE fact_invoices ADD COLUMN tenant_id uuid;
ALTER TABLE fact_payments ADD COLUMN tenant_id uuid;
-- … every fact / dim table

-- B. Index it (BEFORE backfill, so backfill is fast)
CREATE INDEX CONCURRENTLY idx_fact_orders_tenant ON fact_orders (tenant_id);
CREATE INDEX CONCURRENTLY idx_fact_invoices_tenant ON fact_invoices (tenant_id);

-- C. Composite indexes for common scoped queries
CREATE INDEX CONCURRENTLY idx_fact_orders_tenant_date ON fact_orders (tenant_id, order_date DESC);
```

### What needs the column

Every table that is **either**:
- A fact table (sales, events, audit logs, anything per-action)
- A dimension that varies per tenant (customers, products, employees — yes, products if pricing is tenant-specific)

Tables that **don't** need it:
- Cross-tenant reference data (countries, currencies, ISO codes)
- Pure system tables (schema_migrations, audit_log if scoped at higher level)
- `tenants` itself (the row IS the tenant)

## Step 2 — Backfill strategy

### Case 2A — Only one tenant exists today

```sql
-- Easy case. Backfill in one statement per table.
BEGIN;
  UPDATE fact_orders SET tenant_id = '<the-one-tenant-uuid>' WHERE tenant_id IS NULL;
  UPDATE fact_invoices SET tenant_id = '<the-one-tenant-uuid>' WHERE tenant_id IS NULL;
  -- … repeat
COMMIT;

-- Verify zero NULLs
SELECT table_name, count(*) FROM (
  SELECT 'fact_orders' AS table_name FROM fact_orders WHERE tenant_id IS NULL
  UNION ALL SELECT 'fact_invoices' FROM fact_invoices WHERE tenant_id IS NULL
) t GROUP BY 1;
-- Expected: zero rows OR all counts = 0
```

### Case 2B — Multiple tenants already mixed in the data

This is the harder case. There needs to be a **disambiguation column** — something already in the row that maps to a tenant. Common patterns:

- `created_by_user_id` → join to `users.tenant_id`
- `account_external_id` → known mapping table
- `subdomain` / `tenant_slug` already in the row → map to `tenants.tenant_id`

```sql
-- Example: orders have user_id; users have tenant_id (already populated)
UPDATE fact_orders fo
SET tenant_id = u.tenant_id
FROM users u
WHERE fo.user_id = u.user_id AND fo.tenant_id IS NULL;

-- Always: verify ZERO unmapped rows BEFORE flipping to NOT NULL
SELECT count(*) FROM fact_orders WHERE tenant_id IS NULL;
-- If non-zero: investigate. Don't NULL → arbitrary value. That's the attack surface.
```

### Step 2c — Flip to NOT NULL

```sql
-- Only after every backfill verifies zero NULLs:
ALTER TABLE fact_orders ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE fact_invoices ALTER COLUMN tenant_id SET NOT NULL;
-- …

-- Add FK to tenants (optional but recommended — catches typos at insert time)
ALTER TABLE fact_orders ADD CONSTRAINT fk_orders_tenant
  FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id);
```

The `NOT NULL` flip is the **point of no return** for backfill. If any row is NULL at this moment, the ALTER fails — which is correct. Fix the backfill, retry.

## Step 3 — Enforcement layer (RLS / semantic-layer scope)

The layer is chosen per the closeness-to-data invariant. See [`./rls-policy-authoring.md`](rls-policy-authoring.md) for the canonical patterns; this skill calls out the **post-hoc-introduction** wrinkles.

### Postgres RLS introduced post-hoc

```sql
-- 1. Enable RLS on each table
ALTER TABLE fact_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_orders FORCE ROW LEVEL SECURITY;

-- 2. Write the policy
CREATE POLICY tenant_isolation_read ON fact_orders
  FOR SELECT USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
CREATE POLICY tenant_isolation_write ON fact_orders
  FOR ALL USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- 3. Role grants — viewer role does NOT have BYPASSRLS
CREATE ROLE viewer_role NOLOGIN;
GRANT SELECT ON fact_orders TO viewer_role;
-- Application connection role assumes viewer_role per request:
-- SET LOCAL ROLE viewer_role; SET LOCAL app.tenant_id = '<jwt-claim>';
```

**Critical:** `FORCE ROW LEVEL SECURITY` — table-owner roles bypass RLS by default. Without `FORCE`, the policy doesn't apply when ELT pipelines or dbt connects as the owner. See [`./rls-policy-authoring.md`](rls-policy-authoring.md) §"Common Postgres RLS footguns".

### Semantic-layer scope rule (Cube example)

```yaml
cubes:
  - name: orders
    access_policy:
      - role: viewer
        conditions:
          - filter:
              member: orders.tenant_id
              operator: equals
              values: ["{ securityContext.tenant_id }"]
```

See [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md) for the full pattern.

### Power BI DAX role

```dax
[Sales Orders RLS] =
  CALCULATETABLE('Sales Orders', 'Sales Orders'[TenantID] = USERNAME())
```

Applied via Workspace → Manage Roles. The embed token's `EffectiveIdentity` carries the username + role name.

## Step 4 — JWT-claim shape migration

The JWT issuer (host application) must add `tenant_id` to its claims **before** the enforcement layer requires it. Otherwise the dashboard breaks at cutover.

### Required claim shape

```json
{
  "sub": "<user_id>",
  "tenant_id": "<tenant-uuid>",     // NEW — required
  "iat": 1716000000,
  "exp": 1716000900,                 // 15 min max
  "iss": "host-app",
  "aud": "dashboard-embed",
  "nonce": "<random-per-request>",
  "allowed_dashboards": ["sales", "ops"]
}
```

`user_id` alone is NEVER enough — the dashboard would have to look up tenant from user, which means the dashboard becomes a tenant-mapping authority. That's the wrong layer. See [`./jwt-embed-issuance.md`](jwt-embed-issuance.md).

### Two-phase issuer update

1. **Phase 1 — additive.** Issuer adds `tenant_id` to every JWT it produces. Existing consumers ignore unknown claims. **Deploy this, validate it appears in test JWTs, leave it running for one full week** to drain any cached tokens.
2. **Phase 2 — enforced.** Enable the enforcement layer (RLS / semantic-layer scope). The claim is now load-bearing.

## Step 5 — Embed-token cutover plan (parallel → cutover → backout)

The cutover is the riskiest step. Plan it as a deploy with a documented backout.

### Stage 5a — Parallel mode (1 day minimum, 1 week preferred)

```
Old code path: still serves single-tenant
New code path: serves multi-tenant with tenant_id enforcement, BEHIND a feature flag
```

Feature flag dispatches the JWT-bearing user to the new path. Start with the consultant's internal account, then 1 friendly client, then 5 clients. Monitor:
- Error rate on the new path
- Query latency (RLS adds ~5-15% overhead with an index; more = missing index)
- Cube pre-agg cache hit rate (per-tenant partitioning changes the cache shape)

### Stage 5b — Cutover

When parallel mode is clean for the chosen window, flip the feature flag for 100% of traffic. **Keep the old code path in the codebase, dormant, for the backout window.**

### Stage 5c — Backout window (minimum 7 days, 14 typical)

If something breaks, flip the feature flag back. The old path still works because `tenant_id` is additive — the data still satisfies the old code's query shape.

After the window passes without incident: remove the old code path, drop dead routes, delete the feature flag. Document the cutover date.

## Step 6 — Cross-boundary denial test (the mandatory pre-flip gate)

**No denial test passing = no cutover.** This is the gate.

```sql
-- tests/multi_tenant_denial.sql
BEGIN;
  -- 1. Insert disjoint data as bypassrls role
  INSERT INTO fact_orders (tenant_id, amount) VALUES
    ('tenant-A-uuid', 100), ('tenant-B-uuid', 200);

  -- 2. Switch to viewer role with RLS enforced
  SET LOCAL ROLE viewer_role;
  SET LOCAL app.tenant_id = 'tenant-A-uuid';

  -- 3. Try to read tenant B's data — expect zero rows
  SELECT count(*) FROM fact_orders WHERE tenant_id = 'tenant-B-uuid';
  -- ASSERT: count = 0. Test fails if non-zero.

  -- 4. Try to insert as tenant A but with tenant-B's id — expect rejection
  INSERT INTO fact_orders (tenant_id, amount) VALUES ('tenant-B-uuid', 999);
  -- ASSERT: error raised. Test fails if insert succeeds.
ROLLBACK;
```

Run in CI on every PR. Mirror for Cube / Power BI per [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md) and [`./jwt-embed-issuance.md`](jwt-embed-issuance.md) §denial-test sections.

## Staged rollout — recommended sequence

| Stage | Scope | Duration | Gate to proceed |
|---|---|---|---|
| Dev / CI | Synthetic tenants A + B | until clean | Denial test passes |
| Internal | Consultant's own tenant only | 24-48h | No errors, latency within 15% baseline |
| 1 friendly client | Pre-warned, fast-rollback channel | 3-5 days | Client signs off; metrics clean |
| 5 clients | Staged 1 per day | 1 week | Aggregate error rate < baseline |
| All clients | Full rollout | n/a | Backout window starts |

## Rollback plan (write it before cutover)

```
TRIGGER (any one):
  - Error rate >2× baseline for 15+ minutes
  - Any cross-tenant data exposure suspected (any report from any user)
  - Query p95 latency >3× baseline for 30+ minutes
  - Denial test starts failing in production canaries

ACTION:
  1. Flip feature flag to old code path (immediate; ~30s propagation)
  2. Verify dashboards loading on old path (≤2 min)
  3. Confirm no PII / cross-tenant exposure during the incident window
  4. Open incident — root-cause before next attempt
  5. If cross-tenant exposure suspected: notify affected tenants per data-processing-agreement
```

## Anti-patterns this skill flags

- **App-code tenant filtering as the load-bearing control** — closeness-to-data violation. App code is acceptable only as redundant layer per [`./rls-policy-authoring.md`](rls-policy-authoring.md).
- **`tenant_id` left nullable in production** — permanent attack surface; an INSERT that forgets the column bypasses every policy
- **Skipping `FORCE ROW LEVEL SECURITY`** — table owners bypass policies; ELT silently runs as owner
- **Adding RLS before backfill completes** — existing queries break on rows where `tenant_id` IS NULL
- **JWT claim added at cutover instead of additively a week prior** — cached tokens reach the new path without the claim → blanket denial
- **No backout window** — "we'll roll back if it breaks" without keeping the old path alive ≠ a backout
- **Denial test only in dev, not in CI** — drift; production diverges
- **Single-tenant deliverable productized without renaming `org_id` / `account_id` to `tenant_id`** — semantics collide; future devs treat the customer's "org" as the tenant boundary
- **Backfilling NULL → an arbitrary value when disambiguation failed** — hides the data-mixing problem; a future audit can't reconstruct the boundary
- **Cube schema deployed without `access_policy`** — see [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md)
- **Cutover during a high-traffic window** — schedule for low-traffic period with a rollback decision-maker on call

## Hygiene checklist before cutover

- [ ] `tenant_id` column on every fact / tenant-varying dim table
- [ ] Backfill verified — zero NULLs across all in-scope tables
- [ ] `NOT NULL` constraint applied (and ALTER did not fail)
- [ ] Composite indexes on `(tenant_id, hot_filter_col)` for known query shapes
- [ ] Enforcement layer (RLS or semantic-layer scope) deployed
- [ ] `FORCE ROW LEVEL SECURITY` set (Postgres) or equivalent on other layers
- [ ] Viewer role has no `BYPASSRLS`
- [ ] JWT issuer includes `tenant_id` claim for at least 1 week before enforcement flip
- [ ] Denial test passing in CI; same test added to production canaries
- [ ] Feature flag deployed; parallel mode validated on internal tenant
- [ ] Rollback plan written; trigger metrics and thresholds defined
- [ ] Backout window calendared (minimum 7 days, 14 preferred)
- [ ] `ravenclaude-core/security-reviewer` sign-off on the cutover
- [ ] Migration notes in the engagement's release notes

## See also

- Skill: [`./rls-policy-authoring.md`](rls-policy-authoring.md) — the enforcement layer this skill introduces
- Skill: [`./jwt-embed-issuance.md`](jwt-embed-issuance.md) — the JWT-claim shape this skill migrates to
- Skill: [`./cube-schema-scaffolding.md`](cube-schema-scaffolding.md) — semantic-layer enforcement when Cube is in the stack
- Skill: [`./dbt-project-scaffolding.md`](dbt-project-scaffolding.md) — propagating `tenant_id` through staging / marts during migration
- Skill: [`./stack-selection.md`](stack-selection.md) — when an engagement crosses from Case B → Case C, triggering this skill
- Template: [`../templates/database-schema-starter.sql`](../templates/database-schema-starter.sql) — the multi-tenant schema endpoint
- Template: [`../templates/rls-cross-tenant-test.sql`](../templates/rls-cross-tenant-test.sql) — the denial test contract
- Knowledge: [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — patterns across Postgres / Snowflake / Power BI
- Upstream review: [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md) §5 (Database)
