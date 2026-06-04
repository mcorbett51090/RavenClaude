{{ config(
    materialized='dynamic_table',
    target_lag="15 minutes",
    snowflake_warehouse='WH_DBT_TRANSFORM',
    on_configuration_change='apply'
) }}

-- =====================================================================
-- dbt-models-bridge-account-xref.sql — conformed cross-system identity spine
-- ---------------------------------------------------------------------
-- Lineage: plugins/data-platform/skills/cross-system-identity-resolution/SKILL.md
--          § "K-12 LEAID matching" — the 7-tier ladder (T0 LEAID exact → T6 reject).
-- Lineage: plugins/data-platform/knowledge/planhat-integration.md
--          § "Keyable hierarchy" — sourceId/externalId on Company.
-- Lineage: build-plan-tier-0.5-real-connectors.md § Step 7.
--
-- READ FIRST: The SPLINK-DRIVEN PYTHON LOADER (T2 + T3 — fuzzy + probabilistic)
-- writes its output to PSM_CONFORMED.MARTS.BRIDGE_ACCOUNT_XREF_SPLINK_RAW.
-- THIS dbt model is the conformed UNION of:
--   (a) the deterministic tiers (T0/T1/T4/T5) computed here in SQL, and
--   (b) the Splink rows from the loader (T2/T3).
--
-- Materialized as a Dynamic Table — Snowflake refreshes every 15 min off the
-- base tables AND the loader's output. The loader is the slow path (Splink
-- training); this DT is the fast path.
--
-- MUST NOT:
--   - Auto-publish a T3 row without reviewed_by IS NOT NULL.
--   - Bypass the bridge with a JOIN ON LOWER(TRIM(name)) anywhere in marts.
--   - Embed LEAID directly in fact tables — use partner_key + dim_partner_lea_link.
--   - Skip the Census Same-Name guard in T2 → T3 downgrade (loader handles it).
-- =====================================================================

-- ---------------------------------------------------------------------
-- T0 — Exact LEAID. Auto-resolve. confidence=1.00.
-- ---------------------------------------------------------------------
with t0_exact as (
    select
        a.sfdc_account_id,
        l.leaid,
        cast(null as varchar)                          as planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        'leaid_exact'                                  as match_method,
        cast(1.00 as float)                            as confidence,
        cast(null as varchar)                          as manual_override_reason,
        cast(null as varchar)                          as overridden_by,
        current_timestamp()                            as last_verified_at
    from {{ ref('stg_salesforce__account') }} a
    join {{ ref('dim_lea') }} l on a.nces_leaid = l.leaid
    where a.nces_leaid is not null
      and l.is_current = true
),

-- ---------------------------------------------------------------------
-- T1 — Deterministic compound (state_fips, normalized name, city).
-- Auto-resolve. confidence=0.95.
-- ---------------------------------------------------------------------
unresolved_after_t0 as (
    select a.*
    from {{ ref('stg_salesforce__account') }} a
    where a.sfdc_account_id not in (select sfdc_account_id from t0_exact)
),

t1_compound as (
    select
        a.sfdc_account_id,
        l.leaid,
        cast(null as varchar)                          as planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        'leaid_compound'                               as match_method,
        cast(0.95 as float)                            as confidence,
        cast(null as varchar)                          as manual_override_reason,
        cast(null as varchar)                          as overridden_by,
        current_timestamp()                            as last_verified_at
    from unresolved_after_t0 a
    join {{ ref('dim_lea') }} l
        on l.state_fips = substring(a.state, 1, 2)   -- assumes state pre-mapped to FIPS
       and {{ ref_normalize_district_name('a.account_name') }} = l.district_name_normalized
       and lower(a.city) = lower(l.city)
    where l.is_current = true
),

-- ---------------------------------------------------------------------
-- T2 + T3 — Splink-driven (fuzzy + probabilistic).
-- Read from the loader's output table. Codex's load-bridge-account-xref.py
-- writes that table; we surface it here with the SKILL's confidence-tier
-- column and respect the Census Same-Name downgrade.
-- ---------------------------------------------------------------------
t2_t3_splink as (
    select
        sfdc_account_id,
        leaid,
        cast(null as varchar)                          as planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        match_method,                                  -- 'leaid_fuzzy_high' | 'leaid_probabilistic'
        confidence,                                    -- 0.70 – 0.95 per loader output
        manual_override_reason,
        overridden_by,
        last_verified_at
    from {{ source('psm_conformed', 'bridge_account_xref_splink_raw') }}
    where match_method in ('leaid_fuzzy_high', 'leaid_probabilistic')
      -- T3 is stewardship-gated: only surface when reviewed.
      and (match_method = 'leaid_fuzzy_high' or overridden_by is not null)
),

-- ---------------------------------------------------------------------
-- T4 — Planhat externalId match (sourceId == sfdc_account_id).
-- Auto-resolve. confidence=1.00.
-- ---------------------------------------------------------------------
t4_external_id as (
    select
        p.sfdc_account_id,
        cast(null as varchar)                          as leaid,
        p.planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        'external_id'                                  as match_method,
        cast(1.00 as float)                            as confidence,
        cast(null as varchar)                          as manual_override_reason,
        cast(null as varchar)                          as overridden_by,
        current_timestamp()                            as last_verified_at
    from {{ ref('stg_planhat__company') }} p
    where p.sfdc_account_id is not null
),

-- ---------------------------------------------------------------------
-- T5 — Email-domain (excluding generic domains).
-- Auto-resolve with audit. confidence=0.75.
-- ---------------------------------------------------------------------
t5_email_domain as (
    select
        c.sfdc_account_id,
        cast(null as varchar)                          as leaid,
        cast(null as varchar)                          as planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        'email_domain'                                 as match_method,
        cast(0.75 as float)                            as confidence,
        cast(null as varchar)                          as manual_override_reason,
        cast(null as varchar)                          as overridden_by,
        current_timestamp()                            as last_verified_at
    from {{ ref('stg_salesforce__contact') }} c
    where split_part(c.email_masked, '@', 2) not in (
        'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'aol.com'
    )
    qualify row_number() over (
        partition by c.sfdc_account_id order by c._loaded_at desc
    ) = 1
),

-- ---------------------------------------------------------------------
-- T6 — Unresolved. Retained, never dropped. account_uid=NULL.
-- ---------------------------------------------------------------------
all_account_ids as (
    select sfdc_account_id from {{ ref('stg_salesforce__account') }}
),

t6_unresolved as (
    select
        a.sfdc_account_id,
        cast(null as varchar)                          as leaid,
        cast(null as varchar)                          as planhat_company_id,
        cast(null as varchar)                          as support_tool_id,
        cast(null as varchar)                          as snowflake_partner_key,
        'unresolved'                                   as match_method,
        cast(0.00 as float)                            as confidence,
        cast(null as varchar)                          as manual_override_reason,
        cast(null as varchar)                          as overridden_by,
        current_timestamp()                            as last_verified_at
    from all_account_ids a
    where a.sfdc_account_id not in (
        select sfdc_account_id from t0_exact union all
        select sfdc_account_id from t1_compound union all
        select sfdc_account_id from t2_t3_splink union all
        select sfdc_account_id from t4_external_id union all
        select sfdc_account_id from t5_email_domain
    )
),

-- ---------------------------------------------------------------------
-- UNION + Splink confidence-tier column (the SKILL's `match_method` enum).
-- Layer the tiers by precedence — T0 wins over T1 wins over T2 etc.
-- Use QUALIFY ROW_NUMBER() to pick the highest-confidence row per partner.
-- ---------------------------------------------------------------------
unioned as (
    select *, 0 as tier_rank from t0_exact union all
    select *, 1 as tier_rank from t1_compound union all
    select *, 2 as tier_rank from t2_t3_splink union all
    select *, 4 as tier_rank from t4_external_id union all
    select *, 5 as tier_rank from t5_email_domain union all
    select *, 6 as tier_rank from t6_unresolved
),

final as (
    select
        -- account_uid is generated deterministically from sfdc_account_id at
        -- the partners mart (Tier 0 schema parity). The bridge stores the
        -- SFDC anchor and the resolved cross-system IDs.
        sfdc_account_id                                as salesforce_id,
        leaid,
        planhat_company_id                             as planhat_id,
        support_tool_id,
        snowflake_partner_key,
        match_method,
        confidence,
        manual_override_reason,
        overridden_by,
        last_verified_at,
        '{{ var("org_uid") }}'                         as org_uid
    from unioned
    qualify row_number() over (
        partition by sfdc_account_id order by tier_rank asc, confidence desc
    ) = 1
)

select * from final
