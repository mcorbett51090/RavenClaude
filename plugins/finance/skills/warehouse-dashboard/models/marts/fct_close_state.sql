-- fct_close_state.sql — REFERENCE (specified, not executed).
-- Grain: entity_id × period. The governed close state + the honesty badges travel to
-- the dashboard verbatim: a green KPI on a self_certified / TB-only package is still
-- self-certified and TB-only, and the dashboard must say so.
select
    entity_id,
    period_id,
    state,
    preparer,
    self_certified,
    package_amount,
    sod_threshold,
    traceability_badge
from {{ ref('stg_close__state') }}
