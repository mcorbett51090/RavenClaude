{{ config(
    materialized='dynamic_table',
    target_lag="15 minutes",
    snowflake_warehouse='WH_DBT_TRANSFORM',
    on_configuration_change='apply',
    cluster_by=['account_uid', "date_trunc('day', usage_date)"]
) }}

-- =====================================================================
-- dbt-models-marts-usage-daily.sql — district-level usage rollups
-- ---------------------------------------------------------------------
-- Lineage:
--   - build-plan-for-codex.md § 3 Step 1 — usage_daily[] field enum.
--   - snowflake-operational-dashboard-patterns.md § "Don't reinvent the warehouse"
--     (zero-copy Snowflake share > new ELT pipeline).
--   - planhat-integration.md § "Configuration steps" (Metrics direction = OUT).
--
-- Reads from the inbound Snowflake share — no copy, no second pipeline.
--
-- Schema (one row per account_uid × usage_date):
--   {account_uid, org_uid, date, active_users, active_teachers,
--    active_admins, messages_sent, messages_received, family_invited,
--    family_activated, family_engagement_rate}
--
-- FERPA discipline:
--   - Rollup grain is DISTRICT, never per-student. The inbound share's
--     contract guarantees the lowest grain is school × user-role × day,
--     never per-student.
--   - active_users column is a count, never a user identifier.
--   - family_engagement_rate is a derived percentage — no PII surfaces.
--
-- Result-cache discipline: WHERE clauses use DATE_TRUNC('day', DATEADD(...))
-- — stable across calls within a day (per snowflake patterns § Result Cache).
-- =====================================================================

with src as (
    select * from {{ source('usage_share', 'usage_daily_district') }}
),

-- Join via the snowflake_partner_key on the bridge (set by the share contract
-- as a deterministic mapping from internal partner_id to the warehouse-shared id).
bridge as (
    select * from {{ ref('bridge_account_xref') }}
    where match_method != 'unresolved'
      and snowflake_partner_key is not null
),

joined as (
    select
        -- account_uid derived from bridge.salesforce_id — same formula as dim_partner.
        regexp_replace(
            concat(
                substring(md5_hex(b.salesforce_id),  1, 8), '-',
                substring(md5_hex(b.salesforce_id),  9, 4), '-4',
                substring(md5_hex(b.salesforce_id), 14, 3), '-8',
                substring(md5_hex(b.salesforce_id), 18, 3), '-',
                substring(md5_hex(b.salesforce_id), 21, 12)
            ),
            '[^0-9a-f-]', ''
        )                                              as account_uid,
        b.org_uid,
        s.usage_date::date                             as usage_date,
        s.active_users_total                           as active_users,
        s.active_users_teacher                         as active_teachers,
        s.active_users_admin                           as active_admins,
        s.messages_sent_total                          as messages_sent,
        s.messages_received_total                      as messages_received,
        s.family_invited_count                         as family_invited,
        s.family_activated_count                       as family_activated,
        -- Snowflake-flavored conditional aggregation. IFF + NULLIF on the divisor
        -- (zero-invitations days produce NULL, NOT a DIV/0 error).
        iff(
            coalesce(s.family_invited_count, 0) = 0,
            cast(null as float),
            round(s.family_activated_count::float / nullif(s.family_invited_count, 0), 4)
        )                                              as family_engagement_rate
    from src s
    join bridge b on s.snowflake_partner_key = b.snowflake_partner_key
),

-- De-dup defensively — share refresh edges can produce double-rows.
final as (
    select *
    from joined
    qualify row_number() over (
        partition by account_uid, usage_date order by active_users desc nulls last
    ) = 1
)

select * from final
