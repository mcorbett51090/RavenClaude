-- stg_close__period.sql — REFERENCE (specified, not executed).
with src as (
    select * from {{ source('finance_close_raw', 'dim_period') }}
)
select
    cast(period_id as varchar)   as period_id,
    cast(fiscal_year as integer) as fiscal_year,
    cast(fiscal_month as integer) as fiscal_month,
    cast(day_count as integer)   as day_count
from src
