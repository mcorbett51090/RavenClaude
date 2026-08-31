# Retrieval-graph design

- **Date:**
- **Corpus question that needs multi-hop or community synthesis:**
- **No-graph baseline result** (metric + date):
- **BM25 / hybrid-vector baseline result** (metric + date) — must have lost:
- **Paradigm check:** III.a vs BM25 handed to `memory-architect-lead`? yes / no
- **Family (design intent, not a winner):** Microsoft GraphRAG / HippoRAG / LightRAG / other
- **Extract:** entity types + **typed** relationships
- **Index architecture:** local / global (communities) / dual-layer
- **Search mode:** local / global / DRIFT / PPR
- **Eval owner:** `ai-rag-engineering` (recall@k, faithfulness) —
- **What this plugin will not do:** pick III.a; run a live store; skip the baseline
