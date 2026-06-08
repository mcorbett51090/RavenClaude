# Rerank when recall is cheap and precision is expensive

**Status:** Pattern
**Domain:** Two-stage retrieval
**Applies to:** `search-relevance-engineering`

---

## Why this exists

Bi-encoders (ANN search) are fast but imprecise: they embed queries and documents independently,
so the relevance signal is approximate. Cross-encoders (rerankers) are slow but precise: they
attend to both query and document jointly, producing a much richer relevance score. The
two-stage pattern exploits the asymmetry — use the bi-encoder's cheapness to recall a candidate
set (top-k), then use the cross-encoder's accuracy to rerank just those candidates.

The failure mode is adding a reranker when the bi-encoder recall is already the bottleneck.
If the relevant document is not in the top-100 candidates, a reranker cannot promote it —
it operates only on what the bi-encoder retrieved. Reranking lipstick on bad recall is waste.

## How to apply

- **Stage 1: fix recall first.** Measure recall@100 (or recall@k where k is the reranker
  input size). If recall@100 < 0.70, improve the bi-encoder (better embeddings, larger k,
  better chunking, add BM25 hybrid) before adding a reranker.
- **Stage 2: add the reranker only when recall is sufficient.** If recall@100 ≥ 0.70 and
  precision@10 is unsatisfactory, add a cross-encoder on the top-k candidates.
- **Size the candidate set to the latency budget.** A cross-encoder on 100 candidates at
  300ms is common; on 20 candidates at 80ms is feasible for tight latency budgets. Measure.
- **Measure the precision + nDCG delta.** A reranker is not free — add it only if
  nDCG@10 improves by ≥ 0.02 on the held-out judgment set.

**Do:**

- Report recall@k alongside the reranker's precision@10 / nDCG@10 — both numbers together
  tell the complete story.
- Start with a lightweight open-weight reranker (ms-marco-MiniLM-L6) before reaching for
  a managed API (Cohere Rerank) — validate the gain before paying for it.
- Document the candidate set size (k) and the latency budget in the architecture spec.

**Don't:**

- Add a reranker as a "search improvement" without measuring bi-encoder recall first.
- Set the candidate set k too small (e.g. k=10) — the reranker cannot surface results it
  never received.
- Use a reranker to mask a fundamentally bad embedding model or chunking strategy.

## Edge cases / when the rule does NOT apply

- Recall@100 is already ≥ 0.95 and precision@10 is also acceptable — no reranker needed.
- A latency budget that makes any cross-encoder inference infeasible (< 50ms total); in this
  case optimize the bi-encoder and accept the precision limit.
- Batch/offline RAG pipelines where latency is unconstrained — in this case a more expensive
  cross-encoder (e.g. full bge-reranker-large) is appropriate.

## See also

- [`./hybrid-beats-pure-vector-for-most-corpora.md`](./hybrid-beats-pure-vector-for-most-corpora.md) — improve recall before adding reranker.
- [`../knowledge/search-retrieval-decision-trees.md`](../knowledge/search-retrieval-decision-trees.md) — the Rerank-or-not tree.
- [`../agents/vector-retrieval-engineer.md`](../agents/vector-retrieval-engineer.md) — reranker design owner.

## Provenance

The bi-encoder + cross-encoder two-stage pattern is documented in the original ColBERT paper
(Khattab & Zaharia, 2020) and the Sentence-Transformers library documentation. The "recall
must be sufficient before reranking" principle is engineering common sense and is repeated in
Cohere, Weaviate, and Pinecone reranker documentation. [verify-at-use for specific model
performance benchmarks]

---

_Last reviewed: 2026-06-08 by `claude`._
