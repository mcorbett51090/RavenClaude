---
name: query-and-index-tuning
description: "Tune queries with evidence: read EXPLAIN (ANALYZE, BUFFERS) first, choose the right index type and column order (B-tree/partial/composite/covering/GIN), rewrite to be sargable, kill N+1 at the SQL level, and keep statistics fresh."
---

# Query & Index Tuning

## Read the plan first
`EXPLAIN (ANALYZE, BUFFERS)` — find seq scans, bad row estimates, expensive sorts/joins. Tune what it shows.

## Right index
| Predicate | Index |
|---|---|
| equality / range | **B-tree** |
| filtered subset | **partial** |
| multi-column (order by selectivity) | **composite** |
| avoid heap fetch | **covering** (INCLUDE) |
| jsonb / full-text | **GIN** |

## Or fix the query
Make it **sargable** (no function on the indexed column), avoid `SELECT *`, batch don't loop, kill N+1 with a join/`IN`.

## Stats
Stale stats cause bad plans — `ANALYZE`/autovacuum tuning fixes more than another index.
