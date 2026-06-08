# Index Sizing & Latency — <index / period>

> Latency budget + index sizing (§3 #4 #7). Math from `../scripts/search_relevance_engineering_calc.py` `latency-budget`/`index-sizing`.

| Stage | p95 latency | Budget | Docs | Shards | Storage |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

**Budget:** tune relevance within the p95 budget; don't chase NDCG into a timeout (§3 #4). Targets carry a source + date (§3 #8).

**Sources:** <URL — retrieval date> for every external benchmark.
