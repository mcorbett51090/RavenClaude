-- stg_close__recon_exception.sql — REFERENCE (specified, not executed).
with src as (
    select * from {{ source('finance_close_raw', 'fct_recon_exception') }}
)
select
    cast(entity_id as uuid)          as entity_id,
    cast(period_id as varchar)       as period_id,
    cast(account as varchar)         as account,
    cast(description as varchar)     as description,
    cast(book_balance as numeric)    as book_balance,
    cast(subledger_balance as numeric) as subledger_balance,
    cast(difference as numeric)      as difference,
    cast(status as varchar)          as status,   -- PASS | FLAG | self-supported
    cast(materiality_threshold as numeric) as materiality_threshold
from src
