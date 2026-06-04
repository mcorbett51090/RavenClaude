{{ config(
    materialized='dynamic_table',
    target_lag="15 minutes",
    snowflake_warehouse='WH_DBT_TRANSFORM',
    on_configuration_change='apply'
) }}

-- =====================================================================
-- dbt-models-marts-priority-score.sql — REFERENCE warehouse-side priority
-- ---------------------------------------------------------------------
-- ┌──────────────────────────────────────────────────────────────────┐
-- │  IMPORTANT CLASSIFICATION NOTICE                                 │
-- │                                                                  │
-- │  Tier 0's bi-report/field-classifications.json marks            │
-- │  `partners[].priority_score` and `priority_breakdown` as         │
-- │  `derived_at_render`.                                            │
-- │                                                                  │
-- │  The export script (export-psm-dashboard.py) MUST emit `null`   │
-- │  for both fields so the renderer can fill them.                  │
-- │                                                                  │
-- │  This file ships as a REFERENCE — it shows the canonical formula │
-- │  for AUDIT purposes (so an engineer can verify weight provenance │
-- │  vs the renderer's implementation) and as the SINGLE SoT for the │
-- │  signal formulas. It is NOT read by the export.                  │
-- │                                                                  │
-- │  Tag: --no-export. Skip in the conformed-mart-set emitted to JSON.│
-- └──────────────────────────────────────────────────────────────────┘
--
-- Lineage:
--   - build-plan-for-codex.md § Step 8 dashboard-priority-score-rubric.md
--     — the 9-signal formulas + caps.
--   - PRIORITY_WEIGHTS config table (snowflake-database-ddl.sql) — single SoT.
--   - dashboard-dead-zones.md — state-keyed suppression of cadence signal.
--
-- Formula:
--   priority_score = round(sum(weights[k] * breakdown[k]) / 100, 2)
-- Each signal is independently capped at 100 by construction (the bucket
-- model in days_overdue_vs_cadence, the explicit min() in escalations, etc.)
-- so the weighted average stays in [0, 100].
-- =====================================================================

with weights as (
    -- Pivot the PRIORITY_WEIGHTS config rows to columns for the score math.
    -- IFF/MAX pattern is the Snowflake-flavored pivot.
    select
        max(iff(weight_key = 'renewal_timing',           weight_value, null))    as w_renewal_timing,
        max(iff(weight_key = 'health_decline',           weight_value, null))    as w_health_decline,
        max(iff(weight_key = 'sentiment_decline',        weight_value, null))    as w_sentiment_decline,
        max(iff(weight_key = 'days_overdue_vs_cadence',  weight_value, null))    as w_days_overdue,
        max(iff(weight_key = 'open_escalations',         weight_value, null))    as w_open_escalations,
        max(iff(weight_key = 'ticket_volume',            weight_value, null))    as w_ticket_volume,
        max(iff(weight_key = 'arr_percentile',           weight_value, null))    as w_arr_percentile,
        max(iff(weight_key = 'top15_bonus',              weight_value, null))    as w_top15_bonus,
        max(iff(weight_key = 'usage_decline',            weight_value, null))    as w_usage_decline
    from {{ source('psm_conformed', 'priority_weights') }}
    where is_current = true
),

partners_with_arr_rank as (
    select
        account_uid,
        org_uid,
        score                                                      as health_score,
        sentiment_score,
        usage_trend_30d_pct,
        open_escalations,
        open_tickets,
        arr,
        contract_end,
        last_touchpoint_at,
        cadence_tier,
        state,
        top15,
        -- arr_percentile signal: percentile_rank() over all partners.
        percent_rank() over (order by arr nulls first) * 100       as arr_percentile_raw
    from {{ ref('dim_partner') }}
),

dead_zones as (
    -- Lookup: is (state, current_date) inside any documented dead zone?
    -- Reads the dashboard-dead-zones.md table loaded as seed.
    select state, is_dead_zone
    from {{ ref('seed_dead_zones_today') }}
),

cadence_days as (
    -- expected cadence_days per tier — from knowledge-file table.
    select cadence_tier, expected_days
    from (
        values
            ('weekly',     7),
            ('bi_weekly', 14),
            ('monthly',   30),
            ('bi_monthly',60),
            ('quarterly', 90),
            ('bi_annual',180)
        as t(cadence_tier, expected_days)
    )
),

breakdown as (
    select
        p.account_uid,
        p.org_uid,

        -- renewal_timing — bucket model. Days until contract_end.
        case
            when p.contract_end is null then 0
            when datediff('day', current_date(), p.contract_end) <= 30  then 100
            when datediff('day', current_date(), p.contract_end) <= 60  then 85
            when datediff('day', current_date(), p.contract_end) <= 90  then 65
            when datediff('day', current_date(), p.contract_end) <= 120 then 40
            when datediff('day', current_date(), p.contract_end) <= 180 then 20
            when datediff('day', current_date(), p.contract_end) <= 270 then 10
            else 0
        end                                                         as b_renewal_timing,

        greatest(0, 100 - coalesce(p.health_score, 100))            as b_health_decline,
        greatest(0, 100 - coalesce(p.sentiment_score, 100))         as b_sentiment_decline,

        -- days_overdue_vs_cadence — bucket model (v3, capped 100 by construction).
        -- Suppressed (→ 0) if state is in a dead-zone today.
        iff(
            coalesce(dz.is_dead_zone, false),
            0,
            case
                when p.last_touchpoint_at is null then 100
                when greatest(0, datediff('day', p.last_touchpoint_at, current_date())
                                 - coalesce(cd.expected_days, 30)) >= 60 then 100
                when greatest(0, datediff('day', p.last_touchpoint_at, current_date())
                                 - coalesce(cd.expected_days, 30)) >= 30 then 80
                when greatest(0, datediff('day', p.last_touchpoint_at, current_date())
                                 - coalesce(cd.expected_days, 30)) >= 14 then 60
                when greatest(0, datediff('day', p.last_touchpoint_at, current_date())
                                 - coalesce(cd.expected_days, 30)) >=  7 then 30
                else 0
            end
        )                                                            as b_days_overdue,

        least(100, coalesce(p.open_escalations, 0) * 25)             as b_open_escalations,
        least(100, coalesce(p.open_tickets, 0) * 10)                 as b_ticket_volume,
        coalesce(p.arr_percentile_raw, 0)                            as b_arr_percentile,
        iff(p.top15 is not null, 100, 0)                             as b_top15_bonus,

        -- usage_decline — corrected v3. Growth → 0; declines clamp to 100.
        iff(
            coalesce(p.usage_trend_30d_pct, 0) >= 0,
            0,
            least(100, abs(p.usage_trend_30d_pct) * 2)
        )                                                            as b_usage_decline

    from partners_with_arr_rank p
    left join dead_zones      dz on p.state         = dz.state
    left join cadence_days    cd on p.cadence_tier  = cd.cadence_tier
),

scored as (
    select
        b.account_uid,
        b.org_uid,
        -- Construct breakdown VARIANT for audit. Renderer recomputes from raw signals.
        object_construct(
            'renewal_timing',          b.b_renewal_timing,
            'health_decline',          b.b_health_decline,
            'sentiment_decline',       b.b_sentiment_decline,
            'days_overdue_vs_cadence', b.b_days_overdue,
            'open_escalations',        b.b_open_escalations,
            'ticket_volume',           b.b_ticket_volume,
            'arr_percentile',          b.b_arr_percentile,
            'top15_bonus',             b.b_top15_bonus,
            'usage_decline',           b.b_usage_decline
        )                                                              as priority_breakdown,
        round(
            (
                w.w_renewal_timing    * b.b_renewal_timing      +
                w.w_health_decline    * b.b_health_decline      +
                w.w_sentiment_decline * b.b_sentiment_decline   +
                w.w_days_overdue      * b.b_days_overdue        +
                w.w_open_escalations  * b.b_open_escalations    +
                w.w_ticket_volume     * b.b_ticket_volume       +
                w.w_arr_percentile    * b.b_arr_percentile      +
                w.w_top15_bonus       * b.b_top15_bonus         +
                w.w_usage_decline     * b.b_usage_decline
            ) / 100.0,
            2
        )                                                              as priority_score
    from breakdown b
    cross join weights w
)

select * from scored
