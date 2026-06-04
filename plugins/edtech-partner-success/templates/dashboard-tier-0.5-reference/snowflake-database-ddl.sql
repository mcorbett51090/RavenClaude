-- =====================================================================
-- snowflake-database-ddl.sql — PSM dashboard Tier 0.5 account objects
-- ---------------------------------------------------------------------
-- Lineage: plugins/data-platform/knowledge/snowflake-operational-dashboard-patterns.md
--   § "Per-warehouse sizing" + § "TL;DR" (XS Standard + AUTO_SUSPEND=60s).
-- Lineage: plugins/data-platform/knowledge/snowflake-psm-dashboard-cost-model.md
--   (the cost shape the warehouse sizes were chosen against).
-- Lineage: plugins/data-platform/knowledge/planhat-integration.md
--   § "Configuration steps (warehouse side)" (USR_PLANHAT_SVC SERVICE user).
--
-- Build-plan reference: build-plan-tier-0.5-real-connectors.md § 3.1 "Snowflake DDL".
--
-- Apply order: this file first; then per-source-schema files; then grants;
-- then clustering keys. See dynamic-tables-and-tasks.sql for the mart layer.
--
-- IDEMPOTENCY: every CREATE uses IF NOT EXISTS or CREATE OR REPLACE where safe.
-- The seed INSERTs are MERGE-style so re-apply does not duplicate.
-- =====================================================================

USE ROLE SECURITYADMIN;

-- ---------------------------------------------------------------------
-- 1. ROLES — minimum-necessary, no ACCOUNTADMIN grants to service roles.
-- ---------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS ROLE_FIVETRAN       COMMENT = 'Fivetran service role — writes to PSM_RAW only.';
CREATE ROLE IF NOT EXISTS ROLE_PLANHAT_SVC    COMMENT = 'Planhat native sync — bidirectional on planhat schemas.';
CREATE ROLE IF NOT EXISTS ROLE_DBT_BUILD      COMMENT = 'dbt build role — owns marts.';
CREATE ROLE IF NOT EXISTS ROLE_DBT_QUERY      COMMENT = 'dbt query role — read-only on marts for tests.';
CREATE ROLE IF NOT EXISTS ROLE_DASHBOARD_RO   COMMENT = 'Read-only dashboard role for the exporter.';

GRANT ROLE ROLE_DBT_BUILD    TO ROLE SYSADMIN;
GRANT ROLE ROLE_DBT_QUERY    TO ROLE SYSADMIN;
GRANT ROLE ROLE_DASHBOARD_RO TO ROLE SYSADMIN;

USE ROLE SYSADMIN;

-- ---------------------------------------------------------------------
-- 2. WAREHOUSES — XS Standard, 60s auto-suspend, initially suspended.
--    Separate warehouses per workload so a noisy dbt build cannot stall
--    the dashboard read path (per snowflake-operational-dashboard-patterns.md
--    § "Per-warehouse sizing").
-- ---------------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS WH_PSM_DASHBOARD
    WAREHOUSE_SIZE      = 'XSMALL'
    WAREHOUSE_TYPE      = 'STANDARD'
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Dashboard read queries + export-psm-dashboard.py.';

CREATE WAREHOUSE IF NOT EXISTS WH_DBT_TRANSFORM
    WAREHOUSE_SIZE      = 'XSMALL'
    WAREHOUSE_TYPE      = 'STANDARD'
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'dbt batch + Dynamic Table refresh.';

CREATE WAREHOUSE IF NOT EXISTS WH_INGEST
    WAREHOUSE_SIZE      = 'XSMALL'
    WAREHOUSE_TYPE      = 'STANDARD'
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Snowpipe + Fivetran landings.';

CREATE WAREHOUSE IF NOT EXISTS WH_PLANHAT_SYNC
    WAREHOUSE_SIZE      = 'XSMALL'
    WAREHOUSE_TYPE      = 'STANDARD'
    AUTO_SUSPEND        = 60
    AUTO_RESUME         = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Planhat native bidirectional sync.';

-- ---------------------------------------------------------------------
-- 3. DATABASES + SCHEMAS — psm_raw (per-source landing) + psm_conformed
--    (staging / intermediate / marts / semantic).
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS PSM_RAW
    COMMENT = 'Raw landings from Fivetran (Salesforce), Planhat native sync, Google Calendar ingest.';

CREATE DATABASE IF NOT EXISTS PSM_CONFORMED
    COMMENT = 'dbt-managed conformed layer — staging, intermediate, marts, semantic.';

USE DATABASE PSM_RAW;
CREATE SCHEMA IF NOT EXISTS SALESFORCE      COMMENT = 'Fivetran SFDC landing — Account, Contact, Opportunity, Contract, SBQQ__*, Case.';
CREATE SCHEMA IF NOT EXISTS PLANHAT         COMMENT = 'Planhat native bidirectional sync — Company, EndUser, License, Metrics.';
CREATE SCHEMA IF NOT EXISTS GOOGLE_CALENDAR COMMENT = 'Google Calendar API events.list landing — read-only first.';
CREATE SCHEMA IF NOT EXISTS USAGE_SHARE     COMMENT = 'Zero-copy share from product analytics account (Tier 0.5 read-only).';

USE DATABASE PSM_CONFORMED;
CREATE SCHEMA IF NOT EXISTS STAGING       COMMENT = 'Typed + renamed staging models.';
CREATE SCHEMA IF NOT EXISTS INTERMEDIATE  COMMENT = 'Per-partner intermediate joins (raw signals only — no priority math).';
CREATE SCHEMA IF NOT EXISTS MARTS         COMMENT = 'Dynamic Tables — dim_partner, fct_*, bridge_account_xref, mart_connector_health.';
CREATE SCHEMA IF NOT EXISTS SEMANTIC      COMMENT = 'MetricFlow semantic layer — measures only, no priority_score.';
CREATE SCHEMA IF NOT EXISTS CONFIG        COMMENT = 'Config tables (PRIORITY_WEIGHTS, RUBRIC_THRESHOLDS).';

-- ---------------------------------------------------------------------
-- 4. CONFIG TABLES — single SoT for weights + thresholds.
--    Read by dbt-models-marts-priority-score.sql AND by the renderer.
--    Source: build-plan-for-codex.md § 3 Step 1 priority_weights{} block.
-- ---------------------------------------------------------------------
USE SCHEMA PSM_CONFORMED.CONFIG;

CREATE TABLE IF NOT EXISTS PRIORITY_WEIGHTS (
    weight_key       VARCHAR(64) NOT NULL,
    weight_value     INTEGER     NOT NULL,
    effective_from   DATE        NOT NULL DEFAULT CURRENT_DATE(),
    effective_to     DATE,
    is_current       BOOLEAN     NOT NULL DEFAULT TRUE,
    notes            VARCHAR(1000),
    CONSTRAINT pk_priority_weights PRIMARY KEY (weight_key, effective_from)
);

-- Seed the v3 PSM-tuned weights. Sum = 100 (asserted by dbt-tests.yml).
-- Source: build-plan-for-codex.md § 3 Step 1 priority_weights{}.
MERGE INTO PRIORITY_WEIGHTS t USING (
    SELECT 'renewal_timing'            AS weight_key, 18 AS weight_value UNION ALL
    SELECT 'health_decline',                            18                   UNION ALL
    SELECT 'sentiment_decline',                         10                   UNION ALL
    SELECT 'days_overdue_vs_cadence',                   10                   UNION ALL
    SELECT 'open_escalations',                          20                   UNION ALL
    SELECT 'ticket_volume',                              5                   UNION ALL
    SELECT 'arr_percentile',                             5                   UNION ALL
    SELECT 'top15_bonus',                                5                   UNION ALL
    SELECT 'usage_decline',                              9
) s
    ON t.weight_key = s.weight_key AND t.is_current = TRUE
WHEN NOT MATCHED THEN INSERT (weight_key, weight_value)
    VALUES (s.weight_key, s.weight_value)
WHEN MATCHED AND t.weight_value <> s.weight_value THEN UPDATE SET weight_value = s.weight_value;

CREATE TABLE IF NOT EXISTS RUBRIC_THRESHOLDS (
    threshold_key     VARCHAR(64) NOT NULL,
    threshold_value   FLOAT       NOT NULL,
    effective_from    DATE        NOT NULL DEFAULT CURRENT_DATE(),
    effective_to      DATE,
    is_current        BOOLEAN     NOT NULL DEFAULT TRUE,
    notes             VARCHAR(1000),
    CONSTRAINT pk_rubric_thresholds PRIMARY KEY (threshold_key, effective_from)
);

-- Seed the band cutoffs + cadence bucket boundaries.
-- Source: build-plan-for-codex.md § Step 8 (signal formulas).
MERGE INTO RUBRIC_THRESHOLDS t USING (
    SELECT 'band_green_low'              AS threshold_key, 75 AS threshold_value UNION ALL
    SELECT 'band_yellow_low',                               55                    UNION ALL
    SELECT 'band_red_high',                                 54                    UNION ALL
    SELECT 'cadence_days_overdue_bucket_1',                  7                    UNION ALL
    SELECT 'cadence_days_overdue_bucket_2',                 14                    UNION ALL
    SELECT 'cadence_days_overdue_bucket_3',                 30                    UNION ALL
    SELECT 'cadence_days_overdue_bucket_4',                 60                    UNION ALL
    SELECT 'renewal_bucket_30d',                            30                    UNION ALL
    SELECT 'renewal_bucket_60d',                            60                    UNION ALL
    SELECT 'renewal_bucket_90d',                            90                    UNION ALL
    SELECT 'renewal_bucket_120d',                          120                    UNION ALL
    SELECT 'renewal_bucket_180d',                          180                    UNION ALL
    SELECT 'splink_t2_jarowinkler_min',                      0.92                 UNION ALL
    SELECT 'splink_t3_probabilistic_min',                    0.70
) s
    ON t.threshold_key = s.threshold_key AND t.is_current = TRUE
WHEN NOT MATCHED THEN INSERT (threshold_key, threshold_value)
    VALUES (s.threshold_key, s.threshold_value)
WHEN MATCHED AND t.threshold_value <> s.threshold_value THEN UPDATE SET threshold_value = s.threshold_value;

-- ---------------------------------------------------------------------
-- 5. ACCEPTANCE QUERIES — copy/paste these to verify after apply:
--
--   SHOW DATABASES LIKE 'PSM_%';
--   SHOW WAREHOUSES LIKE 'WH_%';
--   SHOW ROLES LIKE 'ROLE_%';
--   SHOW SCHEMAS IN DATABASE PSM_RAW;
--   SHOW SCHEMAS IN DATABASE PSM_CONFORMED;
--   SELECT SUM(weight_value) FROM PSM_CONFORMED.CONFIG.PRIORITY_WEIGHTS
--     WHERE is_current = TRUE;   -- expect 100
--
-- End of snowflake-database-ddl.sql.
