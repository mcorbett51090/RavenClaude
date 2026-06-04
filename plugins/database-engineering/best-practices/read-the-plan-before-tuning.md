# Read the query plan before tuning

Always read `EXPLAIN (ANALYZE, BUFFERS)` before adding an index or rewriting a query. The plan shows the real bottleneck — a sequential scan, a bad row estimate from stale statistics, an expensive sort — which is often not what you'd guess. Tuning by assumption is how a schema accumulates five useless indexes and still runs slow.
