-- stg_close__statement_line.sql — REFERENCE (specified, not executed).
with src as (
    select * from {{ source('finance_close_raw', 'fct_close_statement_line') }}
)
select
    cast(entity_id as uuid)    as entity_id,
    cast(period_id as varchar) as period_id,
    cast(statement as varchar) as statement,   -- 'IS' | 'BS'
    cast(section as varchar)   as section,
    cast(line as varchar)      as line,
    cast(amount as numeric)    as amount        -- already presentation-signed upstream
from src
