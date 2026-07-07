-- fct_close_kpi.sql — REFERENCE (specified, not executed).
-- Grain: entity_id × period × metric (long format). value IS NULL where is_na — the
-- KPI's inputs were absent in the package, so it shows 'n/a', never a plugged number.
-- Parity source of truth: entity_dashboard.derive_kpis (ported verbatim by
-- close_package_to_rows.py, which imports and calls it).
select
    entity_id,
    period_id,
    metric,
    value,
    is_na
from {{ ref('stg_close__kpi') }}
