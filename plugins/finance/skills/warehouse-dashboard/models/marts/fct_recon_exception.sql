-- fct_recon_exception.sql — REFERENCE (specified, not executed).
-- Grain: entity_id × period × account. Review-by-exception: FLAG rows are the ones a
-- human reads; PASS / self-supported are carried for completeness + counts.
select
    entity_id,
    period_id,
    account,
    description,
    book_balance,
    subledger_balance,
    difference,
    status,
    materiality_threshold
from {{ ref('stg_close__recon_exception') }}
