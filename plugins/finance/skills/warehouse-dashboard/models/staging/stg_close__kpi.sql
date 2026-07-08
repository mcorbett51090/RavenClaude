-- stg_close__kpi.sql — REFERENCE (specified, not executed).
-- Long-format KPI fact: one row per (entity, period, metric). value is NULL when
-- is_na is true — the honest 'n/a' carried through from derive_kpis, never a plug.
with src as (
    select * from {{ source('finance_close_raw', 'fct_close_kpi') }}
)
select
    cast(entity_id as uuid)    as entity_id,
    cast(period_id as varchar) as period_id,
    cast(metric as varchar)    as metric,
    cast(value as numeric)     as value,
    cast(is_na as boolean)     as is_na
from src
