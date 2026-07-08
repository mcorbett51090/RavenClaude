-- close_rls_policies.sql — Postgres Row Level Security for the finance close marts.
--
-- REFERENCE ARTIFACT — specified, NOT executed. There is no Postgres in this repo;
-- this file is the enforcement contract a consumer deploys (via CI, per
-- data-platform `rls-policy-authoring`). It is a security_review_target: it MUST get
-- ravenclaude-core/security-reviewer sign-off before any real deployment.
--
-- THE FINANCE DELTA vs data-platform's scalar tenant_id: a controller owns a
-- PORTFOLIO of entities, so the session GUC is an ARRAY (`app.entity_ids`), and the
-- predicate is `entity_id = ANY(...::uuid[])` — an IN over the granted set — not a
-- scalar equality. The array is set per request from the embed token's
-- allowed_entities[] claim (resolved by scripts/entity_rls.py). closeness-to-data
-- invariant: the load-bearing cut lives HERE (or in Cube's access_policy for a
-- semantic-layer-fronted stack), never in the rendering layer.
--
-- HONEST CAVEAT: reference implementation, not a live-verified control. Enforcement
-- is specified here, not exercised (no warehouse). A real deployment needs the IdP
-- that issues the signed token, the CI that deploys + denial-tests these policies,
-- and security-reviewer sign-off.

-- ---------------------------------------------------------------------------
-- 1. Roles. The BI tool / Cube connects as the QUERY role — it must NOT hold
--    BYPASSRLS (that would silently skip every policy below). The ELT/dbt BUILD
--    role rebuilds the marts and DOES hold BYPASSRLS by necessity; the two are
--    deliberately different accounts (data-platform dbt-project-scaffolding).
-- ---------------------------------------------------------------------------
CREATE ROLE finance_close_query_role NOLOGIN NOBYPASSRLS;   -- viewer-facing; RLS enforced
CREATE ROLE finance_close_build_role NOLOGIN BYPASSRLS;     -- ELT/dbt only; never serves a viewer
GRANT USAGE ON SCHEMA analytics TO finance_close_query_role;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO finance_close_query_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics
  GRANT SELECT ON TABLES TO finance_close_query_role;

-- ---------------------------------------------------------------------------
-- 2. Per-request tenant context. The app sets the granted portfolio for THIS
--    request only (SET LOCAL — never SET, or a pooled connection leaks it to the
--    next viewer). The value is the resolved allowed_entities[] as a uuid[] literal.
--        SET LOCAL app.entity_ids = '{aaaa...,cccc...}';
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- 3. Enable + FORCE RLS and attach the array-membership read policy to every
--    entity-scoped fact/dim. FORCE so the table owner is not exempt. dim_period is
--    intentionally omitted — a fiscal period is not tenant-secret.
--    `current_setting('app.entity_ids', true)` -> NULL when unset (missing_ok=true),
--    and an empty-string GUC (a lingering SET LOCAL) is coerced to NULL via NULLIF, so
--    unset context DENIES ALL rows (fail-closed), it does not expose the table.
-- ---------------------------------------------------------------------------
ALTER TABLE analytics.dim_entity                ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.dim_entity                FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.dim_entity
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

ALTER TABLE analytics.fct_close_statement_line  ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.fct_close_statement_line  FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.fct_close_statement_line
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

ALTER TABLE analytics.fct_recon_exception       ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.fct_recon_exception       FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.fct_recon_exception
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

ALTER TABLE analytics.fct_flux_movement         ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.fct_flux_movement         FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.fct_flux_movement
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

ALTER TABLE analytics.fct_close_kpi             ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.fct_close_kpi             FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.fct_close_kpi
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

ALTER TABLE analytics.fct_close_state           ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.fct_close_state           FORCE  ROW LEVEL SECURITY;
CREATE POLICY entity_portfolio_read ON analytics.fct_close_state
  FOR SELECT TO finance_close_query_role
  USING (entity_id = ANY (NULLIF(current_setting('app.entity_ids', true), '')::uuid[]));

-- ---------------------------------------------------------------------------
-- 4. Index the tenant column on every entity-scoped table — an ANY(array) predicate
--    still benefits from a btree on entity_id; without it, RLS-filtered reads scan.
-- ---------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS ix_dim_entity_entity_id               ON analytics.dim_entity (entity_id);
CREATE INDEX IF NOT EXISTS ix_fct_stmt_line_entity_id            ON analytics.fct_close_statement_line (entity_id);
CREATE INDEX IF NOT EXISTS ix_fct_recon_entity_id                ON analytics.fct_recon_exception (entity_id);
CREATE INDEX IF NOT EXISTS ix_fct_flux_entity_id                 ON analytics.fct_flux_movement (entity_id);
CREATE INDEX IF NOT EXISTS ix_fct_kpi_entity_id                  ON analytics.fct_close_kpi (entity_id);
CREATE INDEX IF NOT EXISTS ix_fct_state_entity_id                ON analytics.fct_close_state (entity_id);
