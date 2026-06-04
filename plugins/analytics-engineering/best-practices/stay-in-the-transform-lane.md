# Stay in the transform lane

This layer transforms data that has already landed in the analytics warehouse; it does not own ingestion (that's data-platform), the transactional OLTP store (database-engineering), or BI rendering (tableau/data-platform). Reinventing ingestion inside dbt or querying the app's production database for analytics couples concerns that should stay separate and undermines both systems. Transform what's landed; route the rest.
