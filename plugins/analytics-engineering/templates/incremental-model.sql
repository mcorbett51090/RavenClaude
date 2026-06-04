-- Incremental model (pattern)
{{ config(materialized='incremental', unique_key='id', incremental_strategy='merge') }}

select *
from {{ ref('stg_orders') }}
{% if is_incremental() %}
  -- only new/updated rows since last run (+ a late-data buffer)
  where updated_at >= (select coalesce(max(updated_at), '1900-01-01') from {{ this }}) - interval '3 days'
{% endif %}
