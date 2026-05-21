-- staging.stg_quickbooks__customers
-- ---------------------------------------------------------------------------
-- Thin renaming + casting layer over raw_quickbooks.customer.
-- Convention: stg_<source>__<entity>; one model per source entity.
-- Materialized as a view (cheap to recompute).
-- ---------------------------------------------------------------------------

{{ config(materialized='view') }}

with source as (

    select * from {{ source('raw_quickbooks', 'customer') }}

),

renamed as (

    select
        -- IDs + status
        id::text                          as customer_id,
        case when active = true then true else false end as is_active,

        -- Names + display
        display_name::text                as display_name,
        given_name::text                  as first_name,
        family_name::text                 as last_name,
        company_name::text                as company_name,

        -- Contact
        primary_email_addr::text          as email,
        primary_phone::text               as phone,

        -- Billing address (flattened for ease)
        bill_addr_line1::text             as billing_address_line1,
        bill_addr_city::text              as billing_city,
        bill_addr_country_sub_division_code::text as billing_state,
        bill_addr_postal_code::text       as billing_postal_code,

        -- Financials
        balance::numeric(18,2)            as outstanding_balance,
        currency_ref_value::text          as currency_code,

        -- Audit / change tracking
        meta_data_create_time::timestamptz as created_at,
        meta_data_last_updated_time::timestamptz as updated_at,
        _airbyte_extracted_at::timestamptz as _airbyte_extracted_at

    from source

)

select * from renamed
