-- =====================================================================
-- dynamic-tables-and-tasks.sql — Dynamic Table cascade for the marts
-- ---------------------------------------------------------------------
-- Lineage:
--   - plugins/data-platform/knowledge/snowflake-operational-dashboard-patterns.md
--     § "Layer pick — Dynamic Tables now dominate" + § "dbt + Dynamic Tables".
--   - plugins/data-platform/knowledge/snowflake-psm-dashboard-cost-model.md
--     (the 15-min target_lag cost shape).
--   - build-plan-tier-0.5-real-connectors.md § Step 9 + § Step 10 marts.
--
-- WHY THIS FILE EXISTS IN ADDITION TO dbt models:
--   dbt's dynamic_table materialization handles the simple case. This file
--   covers the cross-DT TASK DAG (DOWNSTREAM chaining) and the periodic
--   FORCE REFRESH used by the export script when the renderer asks for a
--   no-cache run. Apply AFTER `dbt build` to wire downstream chaining.
--
-- COST SHAPE (XS Standard, AUTO_SUSPEND=60s):
--   - 15-min lag → ~96 refreshes/day per DT
--   - Real-world dashboards with 6 DTs: ~$15/day idle baseline + per-refresh
--     compute (typically <$30/day for a 25-partner shape).
--   - Lowering to 1-min lag is documented to spike ~5–10× — DO NOT DO IT
--     without a corresponding cost-model update.
--
-- MUST NOT:
--   - Use TARGET_LAG = '1 minute' anywhere.
--   - Chain a TASK off a DT — TASKS run on cron; DTs are downstream-of-each-other.
--   - Run a TASK that calls a stored procedure with side effects on the same
--     warehouse as the dashboard. Use WH_DBT_TRANSFORM (sibling warehouse).
-- =====================================================================

USE ROLE ROLE_DBT_BUILD;
USE WAREHOUSE WH_DBT_TRANSFORM;
USE DATABASE PSM_CONFORMED;
USE SCHEMA MARTS;

-- ---------------------------------------------------------------------
-- 1. ROOT REFRESH SCHEDULE — the staging-side DTs feed the marts DTs
--    via DOWNSTREAM chaining. Each DT is independently declared by dbt;
--    DOWNSTREAM is set here to wire the chain.
--
--    Snowflake refreshes a DOWNSTREAM-lag DT only when an upstream DT
--    refreshes — no separate cron. This is the cheap path.
-- ---------------------------------------------------------------------

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.BRIDGE_ACCOUNT_XREF
    SET TARGET_LAG = '15 minutes'
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.DIM_PARTNER
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.DIM_CONTRACT
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.FCT_PARTNER_HEALTH
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.FCT_SUPPORT_TICKET
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.FCT_CALENDAR_EVENT
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.FCT_RENEWAL_PIPELINE
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.TIMELINE_EVENTS
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.USAGE_DAILY
    SET TARGET_LAG = '15 minutes'   -- root for the snowflake-share chain
        WAREHOUSE   = WH_DBT_TRANSFORM;

ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.USAGE_DAILY_SCHOOL
    SET TARGET_LAG = DOWNSTREAM
        WAREHOUSE   = WH_DBT_TRANSFORM;

-- mart_connector_health refreshes more aggressively because the
-- three-state badge (Live/Stale/Paused) depends on it.
ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.MART_CONNECTOR_HEALTH
    SET TARGET_LAG = '5 minutes'
        WAREHOUSE   = WH_DBT_TRANSFORM;

-- ---------------------------------------------------------------------
-- 2. FORCE-REFRESH TASK — the export script can call this directly to
--    bypass the 15-min cadence. Used by the renderer's "fetch fresh"
--    button. Cron-scheduled hourly as a safety net in case a DOWNSTREAM
--    chain breaks (the canary).
-- ---------------------------------------------------------------------

CREATE OR REPLACE TASK PSM_CONFORMED.MARTS.TASK_FORCE_REFRESH_HOURLY
    WAREHOUSE = WH_DBT_TRANSFORM
    SCHEDULE  = 'USING CRON 0 * * * * UTC'   -- top of every hour
    COMMENT   = 'Safety-net force-refresh. Real cadence is the 15-min DT lag.'
AS
    -- ALTER ... REFRESH cascades to all DOWNSTREAM DTs.
    ALTER DYNAMIC TABLE PSM_CONFORMED.MARTS.BRIDGE_ACCOUNT_XREF REFRESH;

ALTER TASK PSM_CONFORMED.MARTS.TASK_FORCE_REFRESH_HOURLY RESUME;

-- ---------------------------------------------------------------------
-- 3. OBSERVABILITY — wire DT refresh history to an audit view so failures
--    are not silent (per snowflake patterns § Common gotchas #8).
-- ---------------------------------------------------------------------

CREATE OR REPLACE VIEW PSM_CONFORMED.MARTS.V_DT_REFRESH_HEALTH AS
SELECT
    name                                  AS dt_name,
    state,
    refresh_action,
    refresh_start_time,
    refresh_end_time,
    DATEDIFF('second', refresh_start_time, refresh_end_time) AS refresh_seconds,
    error_message
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
WHERE name LIKE 'PSM_CONFORMED.MARTS.%'
  AND refresh_start_time >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
ORDER BY refresh_start_time DESC;

-- ---------------------------------------------------------------------
-- 4. ACCEPTANCE QUERIES (run after apply):
--
--   SHOW DYNAMIC TABLES IN SCHEMA PSM_CONFORMED.MARTS;
--   -- expect 11 rows, target_lag 15min / 5min / DOWNSTREAM mix.
--
--   SELECT * FROM V_DT_REFRESH_HEALTH WHERE state != 'SUCCEEDED';
--   -- expect 0 rows for the trailing 24h.
--
--   SHOW TASKS LIKE 'TASK_FORCE_REFRESH_HOURLY' IN SCHEMA PSM_CONFORMED.MARTS;
--   -- expect state = 'started'.
-- ---------------------------------------------------------------------

-- End of dynamic-tables-and-tasks.sql.
