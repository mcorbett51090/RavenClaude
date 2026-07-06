-- stg_close__entity.sql — REFERENCE (specified, not executed).
-- Staging: rename/cast only, one model per source table (dbt layer rule). The
-- entity_id is the tenant boundary carried all the way to the RLS predicate.
with src as (
    select * from {{ source('finance_close_raw', 'dim_entity') }}
)
select
    cast(entity_id as uuid)      as entity_id,
    cast(entity_name as varchar) as entity_name,
    cast(functional_currency as varchar) as functional_currency
from src
