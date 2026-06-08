---
description: "Design and implement a lexical, vector, or hybrid (BM25 + dense + RRF) retrieval pipeline — from corpus analysis through store selection, index mapping, query path, and hybrid fusion. Produces an integration-ready architecture spec."
---

# Lexical, Vector, and Hybrid Retrieval

**Purpose:** turn a corpus + query analysis into a concrete, integration-ready retrieval
pipeline — the right retrieval mode (lexical / dense / hybrid), the right store, the index
mapping, and the query path including optional hybrid fusion.

---

## Operating loop

1. **Characterise the corpus and query mix.**
   - What fraction of queries are exact-match (product codes, names, IDs)?
   - What fraction are semantic or conceptual?
   - What is the document mutation rate (determines freshness SLA)?
   - What is the vocabulary size and domain specificity?

2. **Traverse the retrieval-mode decision tree.**
   Walk the `Lexical vs Vector vs Hybrid` tree in
   [`../../knowledge/search-retrieval-decision-trees.md`](../../knowledge/search-retrieval-decision-trees.md).
   Land on `lexical-only` / `vector-only` / `hybrid` before continuing.

3. **Select the store.**
   - Lexical-primary → Elasticsearch / OpenSearch (native BM25, kNN support, ops-mature).
   - Vector-primary (no lexical need, low ops budget) → pgvector (in Postgres, near-zero ops)
     or a dedicated store (Pinecone / Weaviate / Qdrant / Milvus) when ANN scale or filtering
     complexity exceeds what pgvector handles.
   - Hybrid-required → Elasticsearch / OpenSearch (native sparse + dense in one query).

4. **Design the index mapping.**
   - For lexical: field types (`text` with correct analyzer, `keyword` for facets), multi-field
     mappings (analyzed + raw), `similarity` setting for BM25.
   - For vector: `dense_vector` field (dims, similarity metric: `cosine` / `dot_product` /
     `l2_norm`), HNSW index params (`m`, `ef_construction`).
   - For hybrid: both sets of fields in one index.

5. **Design the query path.**
   - Lexical path: `multi_match` with field boosts, `bool` query with `should`/`must`,
     `minimum_should_match`.
   - Dense path: `knn` query with `k` (recall budget) and `num_candidates` (HNSW ef_search
     proxy in Elasticsearch 8+).
   - Hybrid path: run both in parallel, fuse with RRF (`rrf: { window_size: 100, rank_constant:
     60 }`) or linear combination.

6. **Define the evaluation hook.**
   Specify the recall@k and nDCG@k targets. Hand off to `retrieval-evaluation` skill or
   `search-eval-engineer` for measurement before declaring done.

---

## Anti-patterns

- Defaulting to vector-only without checking whether the corpus has exact-match query types.
- Designing the index mapping before confirming the retrieval mode.
- Choosing a dedicated vector store when pgvector would serve the load — prefer operational
  simplicity unless throughput, filtering complexity, or multi-tenancy require a dedicated store.
- Running BM25 and ANN in series rather than in parallel — increases latency for no reason.

---

## Output

An index mapping spec (use `templates/index-mapping-spec.md`) + a query-path pseudocode block +
a fusion config (if hybrid) + a measurement plan (recall@k / nDCG@k targets) + a handoff note
for the next specialist.
