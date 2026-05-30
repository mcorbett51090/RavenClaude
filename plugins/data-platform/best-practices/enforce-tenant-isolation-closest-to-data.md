# Enforce tenant isolation at the closest-to-data layer the viewer cannot influence

**Status:** Absolute rule — the load-bearing tenant control is never at the rendering layer, and no stack merges without a cross-boundary denial test.

**Domain:** Multi-tenant security / RLS

**Applies to:** `data-platform`

---

## Why this exists

This is the foundational invariant of the entire plugin. Don't memorize "where RLS lives" — memorize the invariant: **tenant isolation is enforced at the closest-to-data layer the viewer's token cannot influence.** App-code `where tenant_id = ...` on a viewer-facing read path is the classic footgun — it is trivially bypassed and is acceptable only as a *redundant* layer above an enforced one, or in back-end ELT/job code that runs before viewer exposure. The right layer differs by stack, but the invariant does not: raw-Postgres-backed → Postgres RLS; Cube-fronted → `securityContext`; Power BI Embedded (Import) → DAX roles. Retrofitting RLS onto a populated multi-tenant table is far harder than designing it in.

## How to apply

For raw Postgres, enable **and FORCE** RLS, write `USING` *and* `WITH CHECK`, scope per-request with `SET LOCAL`, and index `tenant_id`.

```sql
ALTER TABLE fact_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_orders FORCE  ROW LEVEL SECURITY;   -- table owners bypass without FORCE

CREATE POLICY tenant_iso ON fact_orders
  FOR ALL
  USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

SET LOCAL app.tenant_id = '<jwt-claim-tenant_id>';   -- LOCAL, not SET — pool safety
CREATE INDEX idx_fact_orders_tenant ON fact_orders(tenant_id);
```

**Do:**
- Pick the layer by stack: Cube `access_policy` referencing `{ securityContext.tenant_id }`; Power BI DAX role via `EffectiveIdentity`.
- Ship a **cross-boundary denial test** per stack — issue a token for tenant A, query tenant B, assert zero rows. No test, no merge.
- Source `tenant_id` from a signed JWT claim the host app controls — never from the URL or a query param.

**Don't:**
- Make an app-code filter the load-bearing control on a viewer-facing read.
- Give a viewer-facing role `BYPASSRLS`, or use `SET` instead of `SET LOCAL` behind a connection pool.
- Ship a Cube `cubes/` directory without `access_policy`, or a new `tenant_id` table without `ENABLE` + `FORCE`.

## Edge cases / when the rule does NOT apply

- **Single-tenant deliverable** — no tenant axis means no tenant policy, but **document the assumption** so a future multi-tenant pivot doesn't inherit a silently-missing control.
- **Power BI Embedded DirectQuery + EffectiveIdentity** — the one mode where source-DB RLS *does* participate alongside DAX roles; for the far-more-common Import mode the backstop is role-coverage tests + deny-by-default workspace settings, not Postgres RLS.
- **Back-end ELT/job code** — app-level tenant routing is the application's concern there; the rule governs viewer-facing read paths.

## See also

- [`../knowledge/multi-tenant-rls-patterns.md`](../knowledge/multi-tenant-rls-patterns.md) — the invariant, per-stack enforcement, footguns, defense-in-depth matrix, denial tests
- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — generates RLS policy templates
- [`./issue-short-lived-jwts-for-embeds.md`](./issue-short-lived-jwts-for-embeds.md)

## Provenance

Distilled from `knowledge/multi-tenant-rls-patterns.md` (Last reviewed 2026-05-21) — the foundational invariant, Postgres canonical pattern + footguns, and mandatory cross-boundary denial test — plus `data-platform/CLAUDE.md` house opinion #3 and the §7 hook that flags `CREATE TABLE` with `tenant_id` but no `ENABLE ROW LEVEL SECURITY`.

---

_Last reviewed: 2026-05-30 by `claude`_
