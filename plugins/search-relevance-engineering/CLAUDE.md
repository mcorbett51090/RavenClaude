# Search & Retrieval Engineering Plugin — Team Constitution

> Team constitution for the `search-relevance-engineering` Claude Code plugin — **4** specialist agents for the search and retrieval layer: index architecture and store choice, relevance tuning, vector and hybrid retrieval, and relevance evaluation. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`search-architect`](agents/search-architect.md) | The lexical-vs-vector-vs-hybrid decision, index/store choice, retrieval topology, freshness and scale design, query understanding | "should we use Elasticsearch or Pinecone?", "design our search architecture", "how do we handle real-time indexing at scale?", "what's the right store for our RAG pipeline?" |
| [`relevance-engineer`](agents/relevance-engineer.md) | Relevance tuning (BM25 params, field boosting, synonyms, analyzers), learning-to-rank, query rewriting, precision/recall tradeoffs | "our search results are off", "tune BM25 for our corpus", "add synonyms/stemming", "set up learning-to-rank", "users aren't finding what they want" |
| [`vector-retrieval-engineer`](agents/vector-retrieval-engineer.md) | Embedding model choice, chunking strategy, vector index design (HNSW/IVF), hybrid fusion (RRF), cross-encoder reranking, the RAG retrieval layer | "build our semantic search", "choose an embedding model", "design chunking for our docs", "add a reranker", "wire up the RAG retrieval tier" |
| [`search-eval-engineer`](agents/search-eval-engineer.md) | Relevance judgment sets, offline metrics (nDCG@k, MRR, recall@k), online metrics (CTR, clickthrough), A/B of ranking changes, eval-before-generation discipline | "measure our search quality", "build a judgment set", "A/B test a ranking change", "set up nDCG tracking", "prove retrieval is good before we blame the LLM" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

---

## 2. Cross-cutting house opinions (every agent enforces)

1. **Measure before you tune.** Every relevance change starts with a baseline metric (nDCG@k, MRR, recall@k) against a judgment set. Tuning by intuition is indistinguishable from noise.
2. **Hybrid almost always beats pure-vector for real corpora.** Dense retrieval misses exact-match, rare terms, product codes, and abbreviations. BM25 catches what embeddings miss. Default to hybrid (BM25 + dense + RRF) unless you have evidence the corpus is purely semantic.
3. **Chunk for the question, not the document.** A chunk boundary should maximize the probability that a relevant chunk contains a complete answer to the query. Long chunks hurt precision; too-short chunks hurt recall. Measure.
4. **An embedding model is a choice, not a default.** Domain, language, modality, latency, and cost vary widely across models. Benchmarking on your own corpus is the only honest selection criterion.
5. **Evaluate retrieval separately from generation.** In a RAG system, generation errors and retrieval errors are orthogonal failure modes. Fix retrieval first — a reranker on bad recall is lipstick on a pig.
6. **Rerank when recall is cheap and precision is expensive.** A bi-encoder (ANN) recalls cheaply; a cross-encoder reranks expensively but accurately. Use the two-stage pattern whenever the cost budget allows and precision matters.

---

## 3. Seams (the bridges to neighbouring plugins)

- **The RAG app / generation layer** -> `claude-app-engineering` — this plugin owns retrieval quality; that plugin owns the prompt assembly and generation chain on top of retrieved context.
- **Data pipelines / embedding jobs / index refresh** -> `data-platform` / `ml-engineering` — this plugin designs the indexing strategy; those plugins build the ingestion and featurization pipelines.
- **The API surface in front of search** -> `api-engineering` — this plugin designs the retrieval topology; that plugin designs the API contract and request routing.
- **A/B test significance** -> `applied-statistics` — `search-eval-engineer` sets up the experiment; that plugin runs the significance tests.
- **Infrastructure sizing, cluster ops (Elasticsearch/OpenSearch)** -> `cloud-native-kubernetes` / `infrastructure-engineering` — this plugin specifies shard/replica/node topology; ops owns the cluster lifecycle.
- **Security (PII in an index, access control)** -> `ravenclaude-core/security-reviewer`.

---

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

---

## 5. Knowledge bank

One canonical knowledge file backs all four agents:

- [`knowledge/search-retrieval-decision-trees.md`](knowledge/search-retrieval-decision-trees.md) — Mermaid trees for lexical-vs-vector-vs-hybrid, chunking strategy, and rerank-or-not; plus a dated 2026 capability map of the search/retrieval landscape (Elasticsearch/OpenSearch, pgvector, Pinecone/Weaviate/Qdrant/Milvus, BM25/BM25F, cross-encoder rerankers, RRF). **Traverse the relevant Mermaid tree top-to-bottom before recommending** — the proactive complement to the Capability Grounding Protocol.

---

## 6. Recommended (not bundled) MCP servers

This plugin bundles no MCP server. The genuinely useful servers here — a live Elasticsearch/OpenSearch cluster, a vector store API — are credentialed per-consumer. Secrets stay as a reference (an env-var name), never a literal.

---

## 7. Milestones

- **v0.1.0** — initial build: 4 agents (search-architect, relevance-engineer, vector-retrieval-engineer, search-eval-engineer), 3 skills, 3 commands, 2 templates, 1 decision-tree knowledge bank + 2026 capability map, 6 best-practices, 1 advisory hook, `scripts/search_eval.py` calculator. Created 2026-06-08.
