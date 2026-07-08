-- dim_entity.sql — REFERENCE (specified, not executed). Marts ref staging only.
select entity_id, entity_name, functional_currency
from {{ ref('stg_close__entity') }}
