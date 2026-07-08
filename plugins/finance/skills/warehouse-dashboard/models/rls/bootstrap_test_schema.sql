-- bootstrap_test_schema.sql — minimal materialization of the entity-scoped marts so
-- close_rls_policies.sql + rls_cross_entity_denial_test.sql can run standalone against
-- a throwaway Postgres (CI / a container), WITHOUT the full dbt build.
--
-- In a real deployment the dbt BUILD role owns these tables (data-platform
-- dbt-project-scaffolding); here we create them as the superuser and grant the build
-- role INSERT so the denial test can seed. Only the columns the policy + denial test
-- touch are modelled — this is a security-control fixture, not the production schema.
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_entity
  (entity_id uuid PRIMARY KEY, name text, functional_currency text);
CREATE TABLE IF NOT EXISTS analytics.fct_close_statement_line
  (entity_id uuid, period_id text, statement text, line_key text, amount numeric);
CREATE TABLE IF NOT EXISTS analytics.fct_recon_exception
  (entity_id uuid, period_id text, account text, difference numeric, status text);
CREATE TABLE IF NOT EXISTS analytics.fct_flux_movement
  (entity_id uuid, period_id text, account text, movement numeric);
CREATE TABLE IF NOT EXISTS analytics.fct_close_kpi
  (entity_id uuid, period_id text, metric text, value numeric, is_na boolean);
CREATE TABLE IF NOT EXISTS analytics.fct_close_state
  (entity_id uuid, period_id text, state text, self_certified boolean);
