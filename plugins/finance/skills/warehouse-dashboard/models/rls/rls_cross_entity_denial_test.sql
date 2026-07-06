-- rls_cross_entity_denial_test.sql — the go-live gate for FORCE-RLS.
--
-- REFERENCE ARTIFACT — specified, NOT executed here. This is the cross-boundary
-- denial test data-platform requires of every multi-tenant stack: it MUST return
-- ZERO rows for the ungranted entity, or the build fails. A consumer runs it against
-- a fresh test DB in CI after deploying close_rls_policies.sql. No test passing = no
-- merge. This is a security_review_target.
--
-- The finance twist: the grant is a PORTFOLIO (array), so the test grants entity A
-- only and proves entity B and entity C are BOTH invisible — an over-grant bug (e.g.
-- a scalar predicate, or a missing FORCE) would leak them.

-- 1. Seed disjoint rows for three entities as the BYPASSRLS build role.
SET ROLE finance_close_build_role;
INSERT INTO analytics.fct_close_kpi (entity_id, period_id, metric, value, is_na) VALUES
  ('aaaaaaaa-0000-5000-8000-000000000001', '2026-06', 'revenue', 1000000, false),
  ('bbbbbbbb-0000-5000-8000-000000000002', '2026-06', 'revenue', 2000000, false),
  ('cccccccc-0000-5000-8000-000000000003', '2026-06', 'revenue', 3000000, false);
RESET ROLE;

-- 2. Switch to the viewer role (RLS enforced, NO BYPASSRLS) and grant ONLY entity A.
SET ROLE finance_close_query_role;
SET LOCAL app.entity_ids = '{aaaaaaaa-0000-5000-8000-000000000001}';

-- 3a. EXPECTED: exactly 1 row — entity A only.
SELECT count(*) AS granted_rows_expected_1
FROM analytics.fct_close_kpi;

-- 3b. EXPECTED: ZERO rows — an explicit filter for entity B is overridden by RLS.
--     Test FAILS if this is non-zero.
SELECT count(*) AS leaked_rows_expected_0
FROM analytics.fct_close_kpi
WHERE entity_id = 'bbbbbbbb-0000-5000-8000-000000000002';

-- 3c. EXPECTED: ZERO rows — with NO context set, fail-closed denies everything.
RESET app.entity_ids;
SELECT count(*) AS unset_context_rows_expected_0
FROM analytics.fct_close_kpi;

RESET ROLE;
