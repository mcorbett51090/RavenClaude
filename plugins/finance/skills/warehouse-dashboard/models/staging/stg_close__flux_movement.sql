-- stg_close__flux_movement.sql — REFERENCE (specified, not executed).
with src as (
    select * from {{ source('finance_close_raw', 'fct_flux_movement') }}
)
select
    cast(entity_id as uuid)      as entity_id,
    cast(period_id as varchar)   as period_id,
    cast(account as varchar)     as account,
    cast(description as varchar) as description,
    cast(current as numeric)     as current_amount,
    cast(prior as numeric)       as prior_amount,
    cast(movement as numeric)    as movement,
    cast(pct_change as numeric)  as pct_change
from src
