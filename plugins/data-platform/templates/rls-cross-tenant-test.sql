-- ---------------------------------------------------------------------------
-- Cross-tenant denial test
-- ---------------------------------------------------------------------------
-- Companion to templates/database-schema-starter.sql
-- Last reviewed: 2026-05-21
--
-- This test MUST pass (return zero rows in the final SELECT) before any
-- multi-tenant schema goes to production. No test passing = no merge.
--
-- The test:
--   1. Inserts disjoint data for two test tenants as the elt_role (BYPASSRLS)
--   2. Switches to viewer_role (RLS-enforced)
--   3. Impersonates tenant-A via SET LOCAL app.tenant_id
--   4. Attempts to read tenant-B's data
--   5. EXPECTATION: zero rows. Non-zero = RLS broken.
--
-- Run in CI:
--   psql -d test_db -f rls-cross-tenant-test.sql
--   If the final SELECT returns >0 rows, the build fails.
-- ---------------------------------------------------------------------------

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Setup: as elt_role (bypasses RLS), insert two test tenants' data
-- ---------------------------------------------------------------------------
SET ROLE elt_role;

-- Two test tenants (use fixed UUIDs for repeatable testing)
INSERT INTO tenants (id, name, slug) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Test Tenant A', 'test-tenant-a'),
    ('22222222-2222-2222-2222-222222222222', 'Test Tenant B', 'test-tenant-b')
ON CONFLICT (id) DO NOTHING;

-- Disjoint fact data
INSERT INTO fact_orders (tenant_id, order_date, amount) VALUES
    ('11111111-1111-1111-1111-111111111111', '2026-05-01', 100.00),
    ('11111111-1111-1111-1111-111111111111', '2026-05-02', 150.00),
    ('22222222-2222-2222-2222-222222222222', '2026-05-01', 200.00),
    ('22222222-2222-2222-2222-222222222222', '2026-05-02', 250.00);

RESET ROLE;

-- ---------------------------------------------------------------------------
-- 2. Switch to viewer role (RLS enforced)
-- ---------------------------------------------------------------------------
SET ROLE viewer_role;

-- Impersonate tenant A
SET LOCAL app.tenant_id = '11111111-1111-1111-1111-111111111111';

-- ---------------------------------------------------------------------------
-- 3. Positive control: viewer should see tenant A's data
-- ---------------------------------------------------------------------------
SELECT 'Tenant A positive control (expect 2 rows)' AS test_name, count(*) AS row_count
FROM fact_orders
WHERE tenant_id = '11111111-1111-1111-1111-111111111111';

-- ---------------------------------------------------------------------------
-- 4. Negative control: viewer must NOT see tenant B's data
-- ---------------------------------------------------------------------------
-- The CRITICAL assertion. RLS should make this return zero rows
-- regardless of the explicit WHERE clause (because the policy injects
-- WHERE tenant_id = current_setting('app.tenant_id')).
SELECT 'Tenant B cross-tenant denial (expect ZERO rows)' AS test_name, count(*) AS row_count
FROM fact_orders
WHERE tenant_id = '22222222-2222-2222-2222-222222222222';

-- ---------------------------------------------------------------------------
-- 5. CI assertion: the test fails the build if the second count > 0
-- ---------------------------------------------------------------------------
-- This DO block raises an exception if cross-tenant data is visible.
-- The CI step should treat any error here as a hard failure.
DO $$
DECLARE
    visible_count integer;
BEGIN
    SELECT count(*)
      INTO visible_count
      FROM fact_orders
     WHERE tenant_id = '22222222-2222-2222-2222-222222222222';

    IF visible_count > 0 THEN
        RAISE EXCEPTION 'CROSS-TENANT LEAK: viewer_role with app.tenant_id=tenant-A saw % rows from tenant-B. RLS is misconfigured.', visible_count;
    END IF;

    RAISE NOTICE 'Cross-tenant denial test PASSED. viewer_role cannot see other tenants.';
END $$;

RESET ROLE;

-- ---------------------------------------------------------------------------
-- 6. Cleanup
-- ---------------------------------------------------------------------------
SET ROLE elt_role;

DELETE FROM fact_orders
 WHERE tenant_id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222'
 );

DELETE FROM tenants
 WHERE id IN (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222'
 );

RESET ROLE;

COMMIT;

-- ---------------------------------------------------------------------------
-- Refresh triggers for this template:
--   * fact_orders table schema changes
--   * Additional fact tables added to the engagement (replicate this pattern
--     per table — or generalize to a stored proc that walks the catalog)
--   * Postgres major-version change affecting RLS semantics
-- ---------------------------------------------------------------------------
