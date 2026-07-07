-- stg_close__state.sql — REFERENCE (specified, not executed).
with src as (
    select * from {{ source('finance_close_raw', 'fct_close_state') }}
)
select
    cast(entity_id as uuid)          as entity_id,
    cast(period_id as varchar)       as period_id,
    cast(state as varchar)           as state,
    cast(preparer as varchar)        as preparer,
    cast(self_certified as boolean)  as self_certified,
    cast(package_amount as numeric)  as package_amount,
    cast(sod_threshold as numeric)   as sod_threshold,
    cast(traceability_badge as varchar) as traceability_badge
from src
