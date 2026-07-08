-- rls_cross_entity_denial_test.sql — the go-live gate for FORCE-RLS.
--
-- EXECUTED (v0.17.1) against a containerized postgres:16 via run_rls_denial_test.sh —
-- no longer "specified only" for the DB layer. It returns ZERO rows for every
-- ungranted entity, or the build fails. Run it against a fresh test DB in CI after
-- deploying close_rls_policies.sql. No test passing = no merge. Security_review_target.
--
-- The finance twist: the grant is a PORTFOLIO (array), so the test grants entity A
-- only and proves entity B and C are BOTH invisible — an over-grant bug (a scalar
-- predicate, or a missing FORCE) would leak them.
--
-- CRITICAL (fixed v0.17.1): the per-request grant uses SET LOCAL, which only holds
-- INSIDE an explicit transaction. Each query block below is wrapped in BEGIN/COMMIT
-- so the grant actually applies to its SELECT. Running these statements in psql
-- autocommit mode WITHOUT the BEGIN/COMMIT makes SET LOCAL a silent no-op and the
-- test false-fails. In production the app opens one transaction per request and
-- issues SET LOCAL + the queries within it — this mirrors that.

-- 1. Seed disjoint rows for three entities as the BYPASSRLS build role.
SET ROLE finance_close_build_role;
INSERT INTO analytics.fct_close_kpi (entity_id, period_id, metric, value, is_na) VALUES
  ('aaaaaaaa-0000-5000-8000-000000000001', '2026-06', 'revenue', 1000000, false),
  ('bbbbbbbb-0000-5000-8000-000000000002', '2026-06', 'revenue', 2000000, false),
  ('cccccccc-0000-5000-8000-000000000003', '2026-06', 'revenue', 3000000, false);
RESET ROLE;

-- 2a. Grant ONLY entity A. EXPECTED: exactly 1 row (entity A).
BEGIN;
  SET ROLE finance_close_query_role;
  SET LOCAL app.entity_ids = '{aaaaaaaa-0000-5000-8000-000000000001}';
  SELECT 'RESULT granted=' || count(*) || ' (expect 1)' FROM analytics.fct_close_kpi;
  -- 2b. EXPECTED: ZERO — an explicit filter for entity B is overridden by RLS.
  SELECT 'RESULT leaked=' || count(*) || ' (expect 0)'
  FROM analytics.fct_close_kpi WHERE entity_id = 'bbbbbbbb-0000-5000-8000-000000000002';
COMMIT;

-- 3. No context set at all. EXPECTED: ZERO — fail-closed denies everything.
BEGIN;
  SET ROLE finance_close_query_role;
  SELECT 'RESULT unset=' || count(*) || ' (expect 0)' FROM analytics.fct_close_kpi;
COMMIT;

-- 4. Explicit empty portfolio '{}'. EXPECTED: ZERO — an empty grant is not "see all".
BEGIN;
  SET ROLE finance_close_query_role;
  SET LOCAL app.entity_ids = '{}';
  SELECT 'RESULT empty=' || count(*) || ' (expect 0)' FROM analytics.fct_close_kpi;
COMMIT;

-- 5. A real portfolio {A,C}. EXPECTED: exactly 2 — the array-claim IN over the granted
--    set (the finance delta vs a scalar tenant_id). B stays invisible.
BEGIN;
  SET ROLE finance_close_query_role;
  SET LOCAL app.entity_ids = '{aaaaaaaa-0000-5000-8000-000000000001,cccccccc-0000-5000-8000-000000000003}';
  SELECT 'RESULT portfolio_AC=' || count(*) || ' (expect 2)' FROM analytics.fct_close_kpi;
COMMIT;
