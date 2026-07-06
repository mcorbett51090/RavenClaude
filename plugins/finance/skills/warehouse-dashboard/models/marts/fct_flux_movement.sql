-- fct_flux_movement.sql — REFERENCE (specified, not executed).
-- Grain: entity_id × period × account. Already materiality-suppressed upstream — the
-- mart carries only the lines that MOVED, so a portfolio dashboard reads a handful.
select
    entity_id,
    period_id,
    account,
    description,
    current_amount,
    prior_amount,
    movement,
    pct_change
from {{ ref('stg_close__flux_movement') }}
