-- marts.dim_customer
-- ---------------------------------------------------------------------------
-- Customer dimension — unified across upstream sources (QBO, Stripe, Salesforce,
-- HubSpot). Surrogate key + alternate keys for upstream lookups.
--
-- This is a mart-layer table — materialized as a table for dashboard read perf.
-- Tests + docs in this layer's schema.yml.
-- ---------------------------------------------------------------------------

{{ config(materialized='table') }}

-- Multi-source dimension example. In a real engagement, the consultant would:
--   1. Decide on the source-of-truth per attribute (often QBO for billing,
--      Salesforce for sales pipeline, HubSpot for marketing)
--   2. Build matching/dedup logic appropriate to the engagement (often via
--      a customer-matching key like email or business name)
--   3. Layer engagement-specific attributes (segment, tier, etc.)
--
-- The template below is a placeholder showing the multi-source pattern.

with qbo_customers as (

    select * from {{ ref('stg_quickbooks__customers') }}

),

-- stripe_customers as (
--     select * from {{ ref('stg_stripe__customers') }}
-- ),

-- salesforce_accounts as (
--     select * from {{ ref('stg_salesforce__accounts') }}
-- ),

-- hubspot_companies as (
--     select * from {{ ref('stg_hubspot__companies') }}
-- ),

-- Customer-matching layer would go in models/intermediate/int_customer__match.sql
-- and feed into this mart.

unified as (

    select
        -- Surrogate key (deterministic hash of upstream IDs)
        {{ dbt_utils.generate_surrogate_key([
            "qbo_customers.customer_id"
        ]) }}                                 as customer_sk,

        -- Alternate keys for upstream lookups
        qbo_customers.customer_id            as qbo_customer_id,
        null::text                            as stripe_customer_id,
        null::text                            as salesforce_account_id,
        null::text                            as hubspot_company_id,

        -- Identifying attributes
        qbo_customers.display_name           as display_name,
        coalesce(qbo_customers.company_name,
                 qbo_customers.first_name || ' ' || qbo_customers.last_name) as canonical_name,
        qbo_customers.email                  as email,
        qbo_customers.phone                  as phone,

        -- Address
        qbo_customers.billing_city           as billing_city,
        qbo_customers.billing_state          as billing_state,
        qbo_customers.billing_postal_code    as billing_postal_code,

        -- Financial snapshot
        qbo_customers.outstanding_balance    as outstanding_balance,
        qbo_customers.currency_code          as currency_code,

        -- Status
        qbo_customers.is_active              as is_active,

        -- Engagement-specific (TODO: populate via int_customer__segment if used)
        null::text                           as segment,
        null::text                           as tier,

        -- Audit
        qbo_customers.created_at             as created_at,
        qbo_customers.updated_at             as updated_at,
        current_timestamp                    as dbt_loaded_at

    from qbo_customers

)

select * from unified
