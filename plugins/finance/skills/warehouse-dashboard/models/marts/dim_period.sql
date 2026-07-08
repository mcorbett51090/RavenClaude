-- dim_period.sql — REFERENCE (specified, not executed).
-- A fiscal period is NOT tenant-secret, so this dim is intentionally un-scoped by RLS.
select period_id, fiscal_year, fiscal_month, day_count
from {{ ref('stg_close__period') }}
