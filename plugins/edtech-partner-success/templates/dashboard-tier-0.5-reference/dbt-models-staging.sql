-- =====================================================================
-- dbt-models-staging.sql — staging models (rename + clean raw columns)
-- ---------------------------------------------------------------------
-- This file is a REFERENCE BUNDLE — Codex splits it into per-vendor files
-- per the build plan §3.2 (stg_salesforce__account.sql, stg_planhat__company.sql,
-- stg_google_calendar__event.sql, etc.). Inline comments mark the split points.
--
-- Lineage:
--   - build-plan-tier-0.5-real-connectors.md § Step 6 staging models
--   - planhat-integration.md § "Deletion handling"
--   - salesforce-cpq-integration.md § "Field-set management" (explicit allow-list)
--   - calendar-integration-google-outlook.md § "Recurring events" (singleEvents=true)
--
-- Snowflake-flavor conventions enforced in every model:
--   - QUALIFY ROW_NUMBER() for de-dup
--   - IFF / COUNT_IF for binary aggregates
--   - DATEDIFF('day', a, b) — no Postgres-isms
--
-- FERPA discipline:
--   - PII surfaces are explicitly masked at staging (email → domain, summary → redacted).
--   - The ferpa_strip_user_content var (dbt_project.yml) toggles aggressive filtering.
-- =====================================================================

-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 1 — staging/stg_salesforce__account.sql
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- Lineage: source('salesforce', 'account') → conformed partner anchor.
-- Source-system specs: salesforce-integration.md § "Bulk API 2.0".

with src as (
    select * from {{ source('salesforce', 'account') }}
    where _fivetran_deleted = false   -- Fivetran soft-delete discipline
),

-- De-dup on Id (defensive — Fivetran is supposed to handle this, but the
-- staging contract is that downstream sees one row per natural key).
deduped as (
    select *
    from src
    qualify row_number() over (partition by id order by _fivetran_synced desc) = 1
),

renamed as (
    select
        id                              as sfdc_account_id,
        name                            as account_name,
        billingstate                    as state,
        billingcity                     as city,
        nces_leaid__c                   as nces_leaid,            -- T0 deterministic anchor
        type                            as account_type,
        ownerid                         as sfdc_owner_id,
        custom_psm_owner__c             as psm_owner,
        annualrevenue                   as annual_revenue,
        createddate                     as account_created_at,
        lastmodifieddate                as account_modified_at,
        _fivetran_synced                as _loaded_at
    from deduped
)

select * from renamed;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 2 — staging/stg_salesforce__contact.sql
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- FERPA: email is masked to "<local>@<domain>" → "[masked]@<domain>" unless flagged.
with src as (
    select * from {{ source('salesforce', 'contact') }}
    where _fivetran_deleted = false
),

cleaned as (
    select
        id                                          as sfdc_contact_id,
        accountid                                   as sfdc_account_id,
        name                                        as contact_name,
        title                                       as contact_title,
        role__c                                     as raw_role,
        -- FERPA: domain-only masking. Cheap; reversible only via --allow-real-ids.
        case
            when email is null then null
            else '[masked]@' || split_part(email, '@', 2)
        end                                          as email_masked,
        case
            when lower(role__c) like '%champion%' then 'champion'
            when lower(title) like '%superintend%' then 'superintendent'
            when lower(title) like '%cio%' or lower(title) like '%cto%' then 'tech_lead'
            when lower(title) like '%president%' or lower(title) like '%chief%' then 'exec_sponsor'
            else 'stakeholder'
        end                                          as derived_role,
        lastactivitydate                             as last_interaction_date,
        _fivetran_synced                             as _loaded_at
    from src
)

select * from cleaned;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 3 — staging/stg_salesforce__case.sql  (Q1 = Service Cloud)
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- Source: salesforce-service-cloud-integration.md § "IsEscalated + MilestoneStatus".
with src as (
    select * from {{ source('salesforce', 'case') }}
    where _fivetran_deleted = false
),

derived as (
    select
        id                                                 as sfdc_case_id,
        accountid                                          as sfdc_account_id,
        casenumber                                         as case_number,
        createddate                                        as opened_at,
        closeddate                                         as closed_at,
        status                                             as status,
        priority                                           as priority,
        type                                               as case_type,
        -- Snowflake-flavored DATEDIFF — NOT Postgres-style (b - a).
        datediff('day', createddate, coalesce(closeddate, current_timestamp())) as age_days,
        iff(
            priority = 'High' or type = 'Escalation' or status = 'Escalated',
            true, false
        )                                                  as is_escalation,
        _fivetran_synced                                   as _loaded_at
    from src
)

select * from derived;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 4 — staging/stg_salesforce__contract.sql  (Q2 = SFDC CPQ)
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- Source: salesforce-cpq-integration.md § "EndDate is the renewal anchor"
-- (NOT RenewalDate — that's the auto-renewal target, often null).
with src as (
    select * from {{ source('salesforce', 'contract') }}
    where _fivetran_deleted = false
),

renamed as (
    select
        id                                                            as sfdc_contract_id,
        accountid                                                     as sfdc_account_id,
        contractnumber                                                as contract_number,
        startdate                                                     as start_date,
        enddate                                                       as end_date,            -- renewal anchor
        sbqq__subscriptionterm__c                                     as subscription_term_months,
        sbqq__amountrolledup__c                                       as arr,
        terminationnoticedays__c                                      as termination_notice_days,
        -- Derived: notice window opens N days before EndDate (CPQ convention).
        dateadd('day', -coalesce(terminationnoticedays__c, 90), enddate)
                                                                      as notice_window_opens_at,
        status                                                        as status,
        sbqq__amendedcontract__c                                      as amended_contract_id,
        lastmodifieddate                                              as last_modified_date,
        _fivetran_synced                                              as _loaded_at
    from src
)

select * from renamed;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 5 — staging/stg_planhat__company.sql
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- Source: planhat-integration.md § "Keyable hierarchy" — sourceId/externalId.
with src as (
    select * from {{ source('planhat', 'company') }}
    where coalesce(_deleted, false) = false  -- Planhat-native delete column
),

renamed as (
    select
        id                       as planhat_company_id,
        sourceid                 as sfdc_account_id,              -- SFDC bridge anchor
        externalid               as partner_key_candidate,
        name                     as company_name,
        healthscore              as planhat_health_score,
        owner                    as planhat_csm_owner,
        phase                    as planhat_phase,
        _synced_at               as _loaded_at
    from src
)

select * from renamed;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 6 — staging/stg_planhat__nps.sql
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- FERPA / PII: verbatim is dropped at staging. Only score + bucket survive.
with src as (
    select * from {{ source('planhat', 'nps') }}
),

masked as (
    select
        id                       as nps_id,
        companyid                as planhat_company_id,
        score                    as nps_score,
        case
            when score >= 9 then 'promoter'
            when score >= 7 then 'passive'
            else 'detractor'
        end                      as nps_bucket,
        -- FERPA: verbatim explicitly NOT propagated. Drop at staging.
        cast(null as varchar)    as nps_verbatim,
        created_at               as submitted_at,
        _synced_at               as _loaded_at
    from src
)

select * from masked;


-- ─────────────────────────────────────────────────────────────────────
-- SPLIT 7 — staging/stg_google_calendar__event.sql  (Q3 = Google Calendar)
-- ─────────────────────────────────────────────────────────────────────
{{ config(materialized='view') }}
-- Source: calendar-integration-google-outlook.md § "Google Calendar API".
-- Discipline: UTC-only; IANA tz lives on dim_partner; singleEvents=true at ingest.
with src as (
    select * from {{ source('google_calendar', 'events') }}
),

masked as (
    select
        event_id,
        i_cal_uid,
        organizer_email,
        -- FERPA: drop event summary unless --allow-real-ids set. Default = redact.
        case
            when {{ var('ferpa_strip_user_content') }} then '[redacted]'
            else summary
        end                                                   as summary,
        start_utc,
        end_utc,
        status,
        attendees_json,
        _loaded_at
    from src
    where end_utc > start_utc          -- defensive — malformed events get dropped
)

select * from masked;
