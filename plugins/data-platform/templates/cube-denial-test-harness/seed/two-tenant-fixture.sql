-- ---------------------------------------------------------------------------
-- Two-tenant seed fixture for the cross-tenant denial test harness
-- (FORGE dashboard-top1pct P1-9, 2026-09-03).
--
-- Applied AFTER database-schema-starter.sql by docker-entrypoint-initdb.d's
-- lexical ordering (01-schema.sql, 02-seed.sql — see docker-compose.yml).
-- Fixed UUIDs so the test file can reference tenant-A/tenant-B without a
-- round-trip lookup.
-- ---------------------------------------------------------------------------

INSERT INTO tenants (id, name, slug, status) VALUES
  ('11111111-1111-1111-1111-111111111111', 'Tenant A (Denial Test)', 'tenant-a-denial-test', 'active'),
  ('22222222-2222-2222-2222-222222222222', 'Tenant B (Denial Test)', 'tenant-b-denial-test', 'active')
ON CONFLICT (id) DO NOTHING;

-- Tenant A: two orders, non-zero revenue — this IS the positive control. A
-- denial test that only ever checks "tenant B's result is empty" proves
-- nothing if tenant A's own query is also (wrongly) empty; asserting tenant
-- A's revenue is non-zero first is what makes an empty tenant-B result mean
-- "isolation works", not "the whole pipeline is broken".
INSERT INTO fact_orders (id, tenant_id, order_date, amount, customer_id) VALUES
  ('a1111111-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', CURRENT_DATE - 5, 150.00, NULL),
  ('a1111111-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', CURRENT_DATE - 2, 275.50, NULL)
ON CONFLICT (id) DO NOTHING;

-- Tenant B: one order, distinct nonzero revenue — if isolation is broken,
-- tenant A's cross-tenant query would surface THIS value (425.00), not zero.
INSERT INTO fact_orders (id, tenant_id, order_date, amount, customer_id) VALUES
  ('b2222222-0000-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', CURRENT_DATE - 3, 425.00, NULL)
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Give viewer_role a way to actually log in for the RLS-layer test.
-- ---------------------------------------------------------------------------
-- database-schema-starter.sql's viewer_role is created with `NOINHERIT` and no
-- LOGIN/password — correct for a role a connection pooler impersonates via
-- SET ROLE, but this harness's test connects DIRECTLY as a Postgres role, so
-- it needs LOGIN + a password. CRITICAL: the harness's Postgres compose user
-- (cube_test, from POSTGRES_USER) is the database's initial superuser, and a
-- Postgres superuser ALWAYS bypasses RLS regardless of policy — connecting the
-- RLS-layer test as cube_test would make the assertion pass unconditionally,
-- proving nothing. The test file MUST connect as viewer_role, never cube_test,
-- for its RLS assertions.
ALTER ROLE viewer_role LOGIN PASSWORD 'viewer_role_test_password_not_for_prod';
