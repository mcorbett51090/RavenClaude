# Multi-tenant RLS patterns

> **Last reviewed:** 2026-05-21. Security-critical reference covering Postgres RLS, Cube `securityContext`, Power BI DAX roles, Fabric workspace roles + OneSecurity, Snowflake row-access policies + dynamic data masking, Databricks Unity Catalog row-filters. **Field guidance, not legal/audit advice.** Refresh when: (a) any of the cited mechanisms ships a breaking change, (b) a security incident in the field surfaces a footgun we missed, or (c) Power BI / Fabric / Cube ships material changes to RLS implementation.

## The foundational invariant

**Tenant isolation is enforced at the closest-to-data layer the viewer's token cannot influence — and never at the rendering layer.**

This is the load-bearing rule for the entire plugin. Don't memorize "where RLS lives"; memorize the invariant. The right layer differs by stack:

| Stack | Closest-to-data layer the viewer can't influence | App-code layer |
|---|---|---|
| Raw Postgres + Metabase/Superset against DB | **Postgres RLS** | NEVER load-bearing |
| Cube → Postgres | **Cube `securityContext`** (DB connection is tenant-blind) | NEVER load-bearing |
| Cube → Snowflake/Databricks | **Cube `securityContext`** (warehouse row-access as backstop) | NEVER load-bearing |
| Power BI Embedded (Import) | **DAX role + RBAC** | NEVER load-bearing |
| Power BI Embedded (DirectQuery + EffectiveIdentity) | **DAX role + source DB RLS via passed identity** | NEVER load-bearing |
| Single-tenant deliverable | **No tenant axis** — but document the assumption | n/a |

App-code tenant filters are acceptable only as (a) redundant layers above an enforced one, or (b) in back-end ELT/job code that runs before viewer exposure.

## Postgres RLS — the canonical pattern

```sql
-- 1. Enable + FORCE RLS
ALTER TABLE fact_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_orders FORCE ROW LEVEL SECURITY;

-- 2. Policy with USING + WITH CHECK (both required for FOR ALL)
CREATE POLICY tenant_iso ON fact_orders
  FOR ALL
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- 3. Per-request: SET LOCAL (not just SET) — connection pool safety
SET LOCAL app.tenant_id = '<jwt-claim-tenant_id>';

-- 4. Index on tenant_id (performance — RLS scans whole tables without it)
CREATE INDEX idx_fact_orders_tenant ON fact_orders(tenant_id);
```

### Postgres RLS footguns

1. **`USING` without `WITH CHECK`** on `FOR ALL` — read-policy enforced, write-policy isn't (or vice versa)
2. **Missing `FORCE ROW LEVEL SECURITY`** — table owners bypass RLS by default; without `FORCE`, ELT pipelines connecting as the table owner skip the policy
3. **`SET` without `LOCAL`** — setting persists across the connection; connection pooling = leak
4. **`bypassrls` role attribute** — superusers and roles with BYPASSRLS skip RLS. ELT roles intentionally have it; viewer-facing roles never should
5. **Missing tenant_id index** — production cost surprise; RLS-filtered queries scan whole tables
6. **New table added without policies** — schema-deployment review must check; the hook flags `CREATE TABLE` with `tenant_id` but no `ENABLE ROW LEVEL SECURITY`
7. **Connection pool that doesn't reset `SET LOCAL`** — verify with the pool implementation; PgBouncer transaction pooling is safer than session pooling for this

## Cube `securityContext`

```yaml
cubes:
  - name: orders
    sql_table: fact_orders
    measures:
      - name: total_revenue
        sql: amount
        type: sum
    dimensions:
      - name: tenant_id
        sql: tenant_id
        type: string
    access_policy:
      - role: viewer
        conditions:
          - filter:
              member: orders.tenant_id
              operator: equals
              values:
                - "{ securityContext.tenant_id }"
```

Cube's query planner injects `WHERE tenant_id = '<jwt-claim>'` *before* SQL is generated. DB connection account is intentionally tenant-blind. Footguns:

1. `access_policy` missing from a cube — Cube serves whatever the query asks for
2. Pre-aggregation without `tenant_id` dimension — shared pre-agg = cross-tenant leak
3. Views without their own `access_policy` — propagation isn't always automatic
4. `securityContext` populated client-side (must come from a signed JWT from host app)

## Power BI DAX roles

```dax
[Sales Order Lines RLS] =
  CALCULATETABLE(
    'Sales Order Lines',
    'Sales Order Lines'[TenantID] = USERNAME()
  )
```

Applied via Workspace → Manage Roles → Add Role → DAX filter. The embed token (Azure AD via MSAL with `EffectiveIdentity`) carries role + username. **Service principal connecting the model bypasses any underlying-DB RLS by necessity** — the model needs all tenants' rows to slice per-viewer.

### Power BI Embedded DirectQuery + EffectiveIdentity (the narrow exception)

When the embed uses **DirectQuery** rather than Import, EffectiveIdentity can pass user identity through to the source. In that narrow mode, **DB-level RLS DOES participate** in addition to DAX roles. This is the only Power BI Embedded pattern where Postgres RLS is meaningful.

For Import mode (much more common), the backstop is:
- Role-coverage tests — verify every role evaluates correctly
- Deny-by-default workspace settings — viewers with no role assigned see nothing

## Fabric OneLake (newer than F-SKU pattern)

Fabric workspace roles + OneSecurity row-level — newer than the F-SKU app-owns-data pattern. **As of 2026-05-21:** check [Microsoft Learn](https://learn.microsoft.com/fabric/) for current state before relying on this knowledge file's framing. The general principle (closeness-to-data + token-independent) applies; the specific implementation moves quickly.

## Snowflake / Databricks (warehouse-native row-policy mechanisms)

### Snowflake
- **Row-access policies** + **dynamic data masking** — apply at the table level
- Evaluate `CURRENT_ROLE()` or session-context variables
- The equivalent layer to Postgres RLS for Snowflake

### Databricks
- **Unity Catalog row-filters + column masks**
- Apply at the table level; integrate with workspace identity

**When Cube fronts a warehouse:** Cube's `access_policy` is the primary control; warehouse row-policy is the backstop.

## Defense-in-depth matrix

| Stack | Primary | Backstop |
|---|---|---|
| Raw Postgres + Metabase/Superset | Postgres RLS (`FORCE`) | n/a — DB IS the closest layer |
| Cube → Postgres | Cube `access_policy` | Postgres RLS (Cube connects with tenant-aware role) |
| Cube → Snowflake | Cube `access_policy` | Snowflake row-access policy |
| Cube → Databricks | Cube `access_policy` | Unity Catalog row-filter |
| Power BI Embedded (Import) | DAX role + RBAC | Role-coverage tests + deny-by-default |
| Power BI Embedded (DirectQuery + EffectiveIdentity) | DAX role | Source DB RLS (same identity passes through) |

## Cross-boundary denial test (mandatory per stack)

### Postgres-backed (the template lives in [`../templates/rls-cross-tenant-test.sql`](../templates/rls-cross-tenant-test.sql)):

```sql
-- As bypassrls role, insert two tenants' data
INSERT INTO fact_orders (tenant_id, amount) VALUES
  ('tenant-A', 100.00),
  ('tenant-B', 200.00);

-- Switch to viewer role; impersonate tenant A
SET ROLE viewer_role;
SET LOCAL app.tenant_id = 'tenant-A';

-- Attempt to read tenant B's data
SELECT count(*) FROM fact_orders WHERE tenant_id = 'tenant-B';
-- EXPECTED: 0 rows. Test fails if non-zero.
```

### Cube-backed:

```python
# Issue JWT for tenant A; query for tenant B's data via explicit filter; expect zero
# (Cube's access_policy overrides the explicit filter)
```

### Power BI Embedded:

Role-coverage test in the engagement's CI: enumerate all DAX roles, verify each evaluates correctly against a synthetic dataset.

**No test, no merge.** This applies to every stack, not just Postgres.

## JWT-claim-driven scoping (the source-of-truth for tenant_id)

See [`../skills/jwt-embed-issuance/SKILL.md`](../skills/jwt-embed-issuance/SKILL.md) for the JWT issuance pattern. Key claims:

- `sub` — user
- `tenant_id` — the boundary
- `iat`, `exp` — short-lived (5-15 min)
- `iss`, `aud` — issuer and audience
- Optional: `allowed_dashboards`, `roles` (for Power BI), `nonce`

The tenant_id in the JWT is signed by the host app — **the viewer cannot influence it** (the foundational invariant).

## App-code filters — when acceptable

Acceptable patterns:

1. **Redundant layer above an enforced one** — ORM `where tenant_id = :ctx` IN ADDITION TO RLS
2. **Back-end ELT/job code** — raw landing tables before viewer exposure; tenant routing is the application concern

Unacceptable:

- App-code filter as the load-bearing control on a viewer-facing read path
- "We'll add RLS later" — retrofitting RLS on a populated multi-tenant table is harder than it looks

## Anti-patterns

- `tenant_id` column without `ENABLE` + `FORCE ROW LEVEL SECURITY`
- `USING` without matching `WITH CHECK` on `FOR ALL`
- `SET app.tenant_id` instead of `SET LOCAL app.tenant_id`
- Viewer-facing role with `BYPASSRLS`
- Missing index on `tenant_id`
- Cross-boundary denial test not in CI
- New table added without RLS
- Power BI engagement insisting on Postgres RLS when DAX roles are the right layer (closeness-to-data violation in reverse)
- Cube engagement shipping `cubes/` without `access_policy`
- App-code-only tenant filtering as load-bearing control
- Single-tenant deliverable with undocumented assumption (silent foot-gun for future multi-tenant pivot)

## Refresh triggers

- Postgres major version with RLS-related changes (rare; check release notes)
- Cube ships breaking changes to `access_policy` syntax
- Power BI / Fabric changes RBAC or DAX-role behavior
- Snowflake or Databricks restructures row-policy primitives
- Field incident exposes a footgun not in this file
- Stack we don't currently cover gains meaningful market share (e.g., MotherDuck adds first-class RLS)
