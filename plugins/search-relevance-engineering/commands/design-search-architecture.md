---
description: "Given a corpus and query description, produce a complete retrieval architecture: store selection, retrieval mode (lexical/vector/hybrid), index topology, freshness design, and a handoff spec for the relevance and vector specialists."
argument-hint: "[context, e.g. 'e-commerce catalogue, 2M products, 60% semantic queries, sub-5-second index freshness SLA, existing Postgres']"
---

You are running `/search-relevance-engineering:design-search-architecture`. Use the
`search-architect` discipline and the `lexical-vector-hybrid-retrieval` skill.

## Steps

1. **Characterise corpus and queries** from the argument or by asking for: document count,
   mutation rate, query type distribution (exact-match vs semantic), freshness SLA, and
   existing infrastructure constraints.

2. **Traverse the decision tree.** Walk the `Lexical vs Vector vs Hybrid` and
   `Store selection` sections in `knowledge/search-retrieval-decision-trees.md`
   top-to-bottom. Record the leaf you land on.

3. **Select the store.** Justify the choice against the three alternatives not chosen.
   If the corpus has any exact-match query types, document why a vector-only store is or is not
   adequate.

4. **Sketch the index topology.** Primary shard count (document-count / target-shard-size),
   replica factor, refresh interval, hot/warm tiering if the corpus is time-series. Output an
   `index-mapping-spec.md` filled from `templates/index-mapping-spec.md`.

5. **Design the query path.** For hybrid: BM25 query body, kNN query params, RRF fusion
   config. For lexical-only or vector-only: the appropriate query form.

6. **Freshness design.** Pin the indexing pattern to the SLA:
   - Real-time (< 5s) → event-driven CDC (Debezium / Kafka Connect).
   - Near-real-time (30s–5m) → micro-batch.
   - Batch → daily/nightly window.

7. **Emit handoffs:** relevance-engineer (field boosts, analyzers), vector-retrieval-engineer
   (embedding model, chunking, HNSW params), search-eval-engineer (establish baseline nDCG@k
   before any tuning).

8. Follow the Structured Output Protocol (`ravenclaude-core`) at the end.
