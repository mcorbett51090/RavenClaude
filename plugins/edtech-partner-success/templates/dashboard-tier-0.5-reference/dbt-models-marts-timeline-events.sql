{{ config(
    materialized='dynamic_table',
    target_lag="15 minutes",
    snowflake_warehouse='WH_DBT_TRANSFORM',
    on_configuration_change='apply',
    cluster_by=['account_uid', "date_trunc('day', ts)"]
) }}

-- =====================================================================
-- dbt-models-marts-timeline-events.sql — conformed cross-source events
-- ---------------------------------------------------------------------
-- Lineage:
--   - build-plan-for-codex.md § 3 Step 1 — timeline_events[] field enum.
--   - calendar-integration-google-outlook.md § "Read-only-first".
--   - planhat-integration.md § "Deletion handling".
--
-- Schema:
--   {event_uid, account_uid, org_uid, type, ts, source, summary,
--    source_ref, payload}
--
-- FERPA discipline:
--   - WHERE type != 'user'  when ferpa_strip_user_content=true (default).
--   - summary is already redacted upstream in stg_google_calendar__event
--     (singleEvents=true expansion).
--   - source_ref uses the v3-tightened opaque URI scheme — no `://` past
--     the scheme, no `.` in body, no `//` in body.
-- =====================================================================

with sf_cases as (
    select
        -- Deterministic event_uid via MD5 — preserves idempotency across rebuilds.
        regexp_replace(
            concat(
                substring(md5_hex(sfdc_case_id),  1, 8), '-',
                substring(md5_hex(sfdc_case_id),  9, 4), '-4',
                substring(md5_hex(sfdc_case_id), 14, 3), '-8',
                substring(md5_hex(sfdc_case_id), 18, 3), '-',
                substring(md5_hex(sfdc_case_id), 21, 12)
            ),
            '[^0-9a-f-]', ''
        )                                                 as event_uid,
        sfdc_account_id                                   as src_account_id,
        case
            when is_escalation then 'escalation_opened'
            when status in ('Closed', 'Resolved') then 'ticket_closed'
            else 'ticket_opened'
        end                                               as type,
        opened_at                                         as ts,
        'support'                                         as source,
        concat('Case #', case_number, ' ', status)        as summary,
        -- v3-tightened opaque URI: scheme://[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*
        concat('support://sfdc-case-', regexp_replace(case_number, '[^A-Za-z0-9_-]', '_'))
                                                          as source_ref,
        object_construct(
            'priority', priority,
            'status', status,
            'is_escalation', is_escalation,
            'age_days', age_days
        )                                                 as payload
    from {{ ref('stg_salesforce__case') }}
),

planhat_health_changes as (
    select
        regexp_replace(
            concat(
                substring(md5_hex(concat(planhat_company_id, ts::varchar)),  1, 8), '-',
                substring(md5_hex(concat(planhat_company_id, ts::varchar)),  9, 4), '-4',
                substring(md5_hex(concat(planhat_company_id, ts::varchar)), 14, 3), '-8',
                substring(md5_hex(concat(planhat_company_id, ts::varchar)), 18, 3), '-',
                substring(md5_hex(concat(planhat_company_id, ts::varchar)), 21, 12)
            ),
            '[^0-9a-f-]', ''
        )                                                 as event_uid,
        planhat_company_id                                as src_company_id,
        'sentiment_change'                                as type,
        ts                                                as ts,
        'planhat'                                         as source,
        'NPS bucket change'                               as summary,
        concat('planhat://health-', regexp_replace(planhat_company_id, '[^A-Za-z0-9_-]', '_'))
                                                          as source_ref,
        object_construct(
            'prior_score', prior_score,
            'new_score', new_score,
            'reason', reason,
            -- FERPA: notes/action_plan are stripped at staging; only categorical here.
            'notes', null,
            'action_plan', null
        )                                                 as payload
    from {{ ref('stg_planhat__health_score_history') }}
),

calendar_events as (
    -- FERPA: source 'calendar', NOT type 'user' — explicit allow-list shape.
    select
        regexp_replace(
            concat(
                substring(md5_hex(event_id),  1, 8), '-',
                substring(md5_hex(event_id),  9, 4), '-4',
                substring(md5_hex(event_id), 14, 3), '-8',
                substring(md5_hex(event_id), 18, 3), '-',
                substring(md5_hex(event_id), 21, 12)
            ),
            '[^0-9a-f-]', ''
        )                                                 as event_uid,
        organizer_email                                   as src_organizer_email,
        'touchpoint_meeting'                              as type,
        start_utc                                         as ts,
        'calendar'                                        as source,
        summary                                           as summary,    -- already redacted in staging
        concat('calendar://event-', regexp_replace(event_id, '[^A-Za-z0-9_-]', '_'))
                                                          as source_ref,
        object_construct(
            'duration_min', datediff('minute', start_utc, end_utc),
            'status', status
        )                                                 as payload
    from {{ ref('stg_google_calendar__event') }}
),

-- ---------------------------------------------------------------------
-- Join each cross-source event back to the conformed account_uid via
-- the bridge. Rows without a bridged account land with account_uid=NULL
-- — they are retained (per SKILL Step 5) for the unresolved alert path.
-- ---------------------------------------------------------------------
unioned as (
    select
        e.event_uid,
        b.salesforce_id,
        b.org_uid,
        e.type,
        e.ts,
        e.source,
        e.summary,
        e.source_ref,
        e.payload
    from sf_cases e
    left join {{ ref('bridge_account_xref') }} b
        on e.src_account_id = b.salesforce_id
       and b.match_method != 'unresolved'

    union all
    select
        e.event_uid, b.salesforce_id, b.org_uid, e.type, e.ts, e.source,
        e.summary, e.source_ref, e.payload
    from planhat_health_changes e
    left join {{ ref('bridge_account_xref') }} b
        on e.src_company_id = b.planhat_id
       and b.match_method != 'unresolved'

    union all
    select
        e.event_uid, b.salesforce_id, b.org_uid, e.type, e.ts, e.source,
        e.summary, e.source_ref, e.payload
    from calendar_events e
    left join {{ ref('bridge_account_xref') }} b
        -- Calendar joins via attendee email domain → SFDC contact → account.
        -- Resolved upstream in int_calendar_to_account; for the reference, the
        -- direct join is shown for clarity.
        on e.src_organizer_email = b.support_tool_id   -- placeholder; real join in int_
),

-- ---------------------------------------------------------------------
-- Derive account_uid deterministically from bridge.salesforce_id (same
-- formula as dim_partner — keeps refs consistent).
-- ---------------------------------------------------------------------
final as (
    select
        event_uid,
        case
            when salesforce_id is null then null
            else regexp_replace(
                concat(
                    substring(md5_hex(salesforce_id),  1, 8), '-',
                    substring(md5_hex(salesforce_id),  9, 4), '-4',
                    substring(md5_hex(salesforce_id), 14, 3), '-8',
                    substring(md5_hex(salesforce_id), 18, 3), '-',
                    substring(md5_hex(salesforce_id), 21, 12)
                ),
                '[^0-9a-f-]', ''
            )
        end                              as account_uid,
        org_uid,
        type,
        ts,
        source,
        summary,
        source_ref,
        payload
    from unioned
    -- FERPA filter — strips any inadvertent 'user' type when toggled.
    where (
        not {{ var('ferpa_strip_user_content') }}
        or type != 'user'
    )
)

select * from final
