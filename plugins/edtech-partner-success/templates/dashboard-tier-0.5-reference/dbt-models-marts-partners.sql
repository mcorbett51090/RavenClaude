{{ config(
    materialized='dynamic_table',
    target_lag="15 minutes",
    snowflake_warehouse='WH_DBT_TRANSFORM',
    on_configuration_change='apply',
    cluster_by=['account_uid']
) }}

-- =====================================================================
-- dbt-models-marts-partners.sql — conformed partners mart
-- ---------------------------------------------------------------------
-- Lineage:
--   - build-plan-for-codex.md § Step 1 — partners[] field enumeration.
--   - build-plan-tier-0.5-real-connectors.md § Step 9 — dim_partner.
--   - cross-system-identity-resolution/SKILL.md — bridge join.
--
-- Schema parity with Tier 0's partners[]:
--   {account_uid, org_uid, name, segment, state, arr, contract_start,
--    contract_end, renewal_date, funding_source, owner_psm, sfdc_owner,
--    top15, lifecycle_phase, lifecycle_substage, stage_entered_at,
--    last_touchpoint_at, cadence_tier, sentiment_score, usage_trend_30d_pct,
--    open_escalations, open_tickets, components{6}, score, delta, band,
--    spark[], flags[], play, last_touch, next_qbr, renewal}
--
-- MUST NOT compute priority_score or priority_breakdown here — Tier 0's
-- field-classifications.json says derived_at_render. Renderer fills.
--
-- account_uid is generated deterministically from sfdc_account_id via
-- MD5_BINARY → UUID. This keeps account_uid stable across rebuilds (NOT
-- using uuid_string() which is non-deterministic and would break the
-- result cache).
-- =====================================================================

with bridge as (
    select * from {{ ref('bridge_account_xref') }}
    where match_method != 'unresolved'
),

partner_signals as (
    select * from {{ ref('int_partner_signals') }}
),

current_contract as (
    -- Snowflake-flavor QUALIFY for the latest current contract per partner.
    select * from {{ ref('stg_salesforce__contract') }}
    where status = 'Activated'
    qualify row_number() over (
        partition by sfdc_account_id order by end_date desc
    ) = 1
),

case_rollup as (
    select
        sfdc_account_id,
        count_if(status not in ('Closed', 'Resolved'))     as open_tickets,
        count_if(is_escalation and status not in ('Closed', 'Resolved'))
                                                            as open_escalations
    from {{ ref('stg_salesforce__case') }}
    group by sfdc_account_id
),

last_touch as (
    -- Touchpoint = the most recent of (calendar event with attendee in account
    -- OR Planhat manual log OR SFDC case interaction). Snowflake DATE_TRUNC
    -- ensures result-cache friendliness (per snowflake-operational-dashboard-patterns.md).
    select
        sfdc_account_id,
        max(touch_at) as last_touchpoint_at
    from {{ ref('int_partner_touchpoints') }}
    group by sfdc_account_id
),

derived as (
    select
        -- Deterministic account_uid: MD5 of sfdc_account_id, formatted as UUIDv4.
        -- Lineage: build-plan-for-codex.md § 3 Step 1 (`account_uid` strict UUIDv4
        -- regex). The MD5_HEX is sliced and a '4' is forced at position 13 (UUIDv4
        -- version marker) + '8' at position 17 (UUIDv4 variant marker).
        regexp_replace(
            concat(
                substring(md5_hex(b.salesforce_id),  1, 8), '-',
                substring(md5_hex(b.salesforce_id),  9, 4), '-4',
                substring(md5_hex(b.salesforce_id), 14, 3), '-8',
                substring(md5_hex(b.salesforce_id), 18, 3), '-',
                substring(md5_hex(b.salesforce_id), 21, 12)
            ),
            '[^0-9a-f-]', ''
        )                                                  as account_uid,

        b.org_uid,
        a.account_name                                     as name,
        a.state                                            as state,
        a.account_type                                     as segment,
        a.psm_owner                                        as owner_psm,
        a.sfdc_owner_id                                    as sfdc_owner,

        -- Contract anchors. EndDate is renewal anchor (NOT RenewalDate).
        cc.start_date                                      as contract_start,
        cc.end_date                                        as contract_end,
        cc.end_date                                        as renewal_date,
        cc.arr                                             as arr,

        -- Funding source from a custom SFDC field; renderer falls back to 'other'.
        coalesce(a.funding_source__c, 'other')             as funding_source,

        -- Lifecycle from Planhat phase (joined upstream in int_partner_signals).
        ps.lifecycle_phase,
        ps.lifecycle_substage,
        ps.stage_entered_at,

        lt.last_touchpoint_at,
        ps.cadence_tier,

        -- Sentiment from Planhat NPS most-recent bucket. Score 0–100.
        ps.sentiment_score,

        -- Usage trend — SIGNED percent. Positive = growth.
        ps.usage_trend_30d_pct,

        -- Support counters (Q1 = SFDC Case).
        coalesce(cr.open_tickets, 0)                       as open_tickets,
        coalesce(cr.open_escalations, 0)                   as open_escalations,

        -- 6-key components block — preserved verbatim from Tier 0.
        object_construct(
            'adoption',     ps.component_adoption,
            'touchpoint',   ps.component_touchpoint,
            'outcome',      ps.component_outcome,
            'sentiment',    ps.component_sentiment,
            'champion',     ps.component_champion,
            'usage',        ps.component_usage
        )                                                  as components,

        ps.health_score                                    as score,
        ps.health_score_delta                              as delta,

        -- Band derivation from RUBRIC_THRESHOLDS config table.
        case
            when ps.health_score >= (select threshold_value from {{ source('psm_conformed','rubric_thresholds') }} where threshold_key = 'band_green_low' and is_current) then 'green'
            when ps.health_score >= (select threshold_value from {{ source('psm_conformed','rubric_thresholds') }} where threshold_key = 'band_yellow_low' and is_current) then 'yellow'
            else 'red'
        end                                                as band,

        ps.spark_8w                                        as spark,
        ps.flags                                           as flags,
        ps.next_play                                       as play,
        lt.last_touchpoint_at                              as last_touch,
        ps.next_qbr_at                                     as next_qbr,
        cc.end_date                                        as renewal,

        -- top15 is null unless a curated reason exists.
        ps.top15_obj                                       as top15,

        -- FERPA: priority_score + priority_breakdown EXPLICITLY null here.
        -- field-classifications.json → derived_at_render.
        cast(null as float)                                as priority_score,
        cast(null as object)                               as priority_breakdown,

        -- engagement_score also derived at render — null here.
        cast(null as float)                                as engagement_score

    from {{ ref('stg_salesforce__account') }} a
    join bridge b           on a.sfdc_account_id = b.salesforce_id
    left join current_contract cc on a.sfdc_account_id = cc.sfdc_account_id
    left join case_rollup cr      on a.sfdc_account_id = cr.sfdc_account_id
    left join last_touch lt       on a.sfdc_account_id = lt.sfdc_account_id
    left join partner_signals ps  on a.sfdc_account_id = ps.sfdc_account_id
)

select * from derived
