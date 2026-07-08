-- fct_close_statement_line.sql — REFERENCE (specified, not executed).
-- Grain: entity_id × period × statement × section × line. Amounts are presentation-
-- signed upstream (statement_engine section convention); the mart never re-signs.
select
    entity_id,
    period_id,
    statement,
    section,
    line,
    amount
from {{ ref('stg_close__statement_line') }}
