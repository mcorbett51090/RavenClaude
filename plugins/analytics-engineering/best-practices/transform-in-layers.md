# Transform in staging → intermediate → marts layers

Stage each source (rename, cast, light clean), compose business logic in intermediate models, and expose business-facing facts and dimensions as marts. A single 600-line model that ingests, joins, and aggregates everything is untestable, unownable, and impossible to reuse. Layering makes each transformation small, testable, and traceable through `ref()` lineage.
