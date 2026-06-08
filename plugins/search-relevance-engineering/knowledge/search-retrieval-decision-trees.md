# Search & Retrieval Engineering — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `search-relevance-engineering`. **Traverse the relevant Mermaid
> tree top-to-bottom before recommending** — the proactive complement to the Capability Grounding
> Protocol. Volatile product/version facts carry `[verify-at-use]`; stable algorithmic facts do not.

---

## Decision Tree 1: Lexical vs Vector vs Hybrid

```mermaid
flowchart TD
  A[Does the corpus have exact-match query types?<br/>e.g. product codes, SKUs, IDs, proper nouns,<br/>abbreviations, serial numbers] -->|Yes| B[BM25 is required — these will fail in pure-vector]
  A -->|No — all queries are conceptual / semantic| C{Is the vocabulary large and domain-specific?}
  C -->|Yes, specialized domain e.g. medical, legal, code| D[Consider domain-adapted embeddings<br/>BM25 may still help with jargon]
  C -->|No — general domain, mostly semantic| E[Vector-only is viable<br/>but measure recall on tail queries first]
  B --> F{What fraction of queries are semantic<br/>i.e. need meaning, not exact tokens?}
  F -->|> 30%| G[Hybrid: BM25 + dense embeddings + RRF<br/>Default for mixed corpora]
  F -->|< 30% — overwhelmingly exact-match| H[Lexical-primary with lightweight vector<br/>or pure lexical if no semantic queries at all]
  D --> G
  G --> I[Implement RRF fusion<br/>rank_constant=60, window_size=100]
  H --> J[BM25 with tuned k1/b<br/>+ analyzer for your domain]
  E --> K[Verify: run recall@100 on tail queries<br/>If recall < 0.7, add BM25 fallback]
```

**Leaf rule:** for any corpus with product codes, identifiers, abbreviations, or proper nouns,
pure-vector retrieval will fail on those query types. Hybrid (BM25 + dense + RRF) is the safe
default; pure-vector requires evidence that the corpus has no exact-match query types. Pure
lexical is suitable only for structured catalogue lookup with no semantic queries.

---

## Decision Tree 2: Chunking Strategy

```mermaid
flowchart TD
  A[What is the typical document length?] -->|Short: < 512 tokens e.g. product descriptions, Q&A| B[Single-chunk whole document<br/>No chunking needed — embed the whole doc]
  A -->|Medium: 512–4096 tokens e.g. articles, wiki pages| C{Do documents have structural sections<br/>e.g. headers, H2s, structured fields?}
  A -->|Long: > 4096 tokens e.g. PDFs, books, reports| D[Must chunk — question is how]
  C -->|Yes — sections are meaningful units| E[Section-header chunking<br/>Each section becomes a chunk]
  C -->|No — flowing prose| F[Fixed-stride with overlap<br/>e.g. 256–512 tokens, 10–20% overlap]
  D --> G{Does the query typically ask about<br/>a specific sub-topic or the whole document?}
  G -->|Specific sub-topic| H[Parent-child chunking<br/>Small chunks 128-256 tokens for embedding<br/>Large parent chunk 1024-2048 for context]
  G -->|Whole document summary| I[Hierarchical: embed both summary and chunks<br/>Retrieve by chunk, return parent as context]
  F --> J[Measure: recall@k with chunk size = 256 vs 512<br/>Pick the one with higher recall on your queries]
  E --> J
  H --> J
  I --> J
  B --> K[No chunking — measure recall@20 to verify]
```

**Leaf rule:** chunk size is a corpus + query-specific empirical decision. The most common
mistake is hardcoding 512 tokens without measuring. Run recall@k at 128, 256, and 512 tokens
on a sample of real queries and pick the size that maximises recall on your query distribution.
Long documents almost always benefit from parent-child chunking: embed small chunks (128–256
tokens) for retrieval precision, return the parent context window (1024–2048 tokens) to the
LLM for answer quality.

---

## Decision Tree 3: Rerank-or-not

```mermaid
flowchart TD
  A[What is the current recall@100 of the bi-encoder ANN stage?] -->|< 0.70| B[Fix recall first — reranking cannot rescue<br/>a document that is not in the candidate set<br/>Increase k, tune HNSW, or improve embeddings]
  A -->|>= 0.70| C{Is precision@10 acceptable?}
  C -->|Yes — users are satisfied / nDCG@10 is strong| D[No reranker needed<br/>Monitor as corpus grows]
  C -->|No — too many irrelevant results in top-10| E{What is the latency budget<br/>for the search request?}
  E -->|Tight: < 100ms total| F[Lightweight reranker only<br/>e.g. ms-marco-MiniLM-L6, top-20 candidates<br/>Or skip reranker — optimize bi-encoder instead]
  E -->|Moderate: 100–500ms| G[Cross-encoder on top-50 candidates<br/>e.g. bge-reranker-v2-m3 or Cohere Rerank]
  E -->|Relaxed: > 500ms or async| H[Full cross-encoder on top-100 candidates<br/>e.g. Cohere Rerank 3, bge-reranker-large]
  G --> I[Measure: precision@10 and nDCG@10 before/after<br/>A/B before shipping]
  H --> I
  F --> I
```

**Leaf rule:** a reranker is a precision tool, not a recall tool. If the bi-encoder recall@100
is below 0.70, fix the embedding model or HNSW parameters first — no reranker can retrieve
a document that wasn't in the top-100 candidate set. When recall is sufficient and precision is
not, add a cross-encoder reranker sized to the latency budget. Always measure the precision@10
and nDCG@10 delta before A/B-testing in production.

---

## 2026 Capability Map — Search & Retrieval Landscape

_Retrieved 2026-06-08. Product versions, pricing, and performance benchmarks are volatile —
re-confirm at use. This is orientation, not a procurement recommendation._

| Category | Options (2026) | Notes |
|---|---|---|
| **Lexical + hybrid search (ops-mature)** | **Elasticsearch 8.x** (Elastic, ESRE, native kNN + BM25 + RRF in one query), **OpenSearch 2.x** (AWS-managed, Elasticsearch fork, hybrid search support) | Battle-tested at scale; native hybrid query in Elasticsearch 8.12+; rich analyzer ecosystem; significant ops cost [verify-at-use]. |
| **In-database vector search** | **pgvector** (Postgres extension, HNSW + IVFFlat), **SQLite-vss** (embedded), **Supabase Vector** (hosted pgvector) | Zero extra infra if Postgres is already in stack; HNSW added in pgvector 0.5.0 (2023); suitable for < 10M vectors and moderate query rates [verify-at-use]. |
| **Dedicated vector stores** | **Pinecone** (managed, serverless tier), **Weaviate** (OSS + managed, hybrid BM25+vector native), **Qdrant** (OSS + managed, Rust, payload filtering), **Milvus** (OSS + Zilliz managed, GPU support) | Higher ANN throughput than pgvector at scale; operational overhead vs managed tradeoff; Pinecone serverless removes index pre-sizing [verify-at-use]. |
| **BM25 / lexical scoring** | **BM25** (Elasticsearch/OpenSearch default, k1=1.2 b=0.75), **BM25F** (multi-field BM25 via field boosts in Elasticsearch), **BM25+** (Okapi extension) | BM25 is the standard; BM25F is achieved via field-level boosts in Elasticsearch; BM25+ relevant for very short queries [verify-at-use]. |
| **Bi-encoder embedding models** | **OpenAI text-embedding-3-small / 3-large** (API, 1536 dims), **Cohere Embed v3** (API, 1024 dims), **voyage-large-2-instruct** (API), **E5-large-v2** / **E5-mistral-7b-instruct** (open-weight), **BGE-large-en-v1.5** / **BGE-M3** (open-weight, multilingual) | BGE-M3 and E5-mistral are strong open-weight options; OpenAI 3-small is cost-competitive; domain fine-tuning consistently beats general models on specialized corpora [verify-at-use]. |
| **Cross-encoder rerankers** | **Cohere Rerank 3 / 3.5** (API, managed), **bge-reranker-v2-m3** (open-weight, multilingual), **ms-marco-MiniLM-L6** (fast, open-weight), **Jina Reranker v2** (open-weight) | Cohere Rerank 3 is strong and managed; bge-reranker-v2-m3 is the best open-weight multilingual option as of mid-2026; ms-marco-MiniLM for latency-sensitive pipelines [verify-at-use]. |
| **Hybrid fusion** | **RRF** (Reciprocal Rank Fusion, native in Elasticsearch 8.12+, OpenSearch 2.x), **Linear combination** (weighted sum of BM25 and cosine scores, requires tuned weight) | RRF is parameter-light and empirically robust; linear combination requires a held-out judgment set to tune the weight; default to RRF [verify-at-use]. |
| **Learning-to-rank** | **Elasticsearch LTR plugin** (XGBoost/LambdaMART features from Elasticsearch scores), **XGBoost RankNet/LambdaMART** (standalone), **LightGBM LGBM Ranker** | Requires click logs or judgment sets at scale; LambdaMART is the standard industrial LTR baseline; neural LTR for very large datasets only [verify-at-use]. |
| **Offline eval metrics** | **nDCG@k** (ranking quality, primary), **MRR** (single-relevant-doc queries), **recall@k** (RAG retrieval), **precision@k** | Computed by `scripts/search_eval.py` in this plugin. |
| **Online eval** | **CTR@k** (click-through rate), **mean click position**, **session abandonment rate**, **explicit relevance feedback** | Online metrics lag offline; use both; never use CTR alone. |

> Provenance: Elasticsearch/OpenSearch official docs, BEIR benchmark results, Cohere/OpenAI
> embedding model pages, pgvector GitHub, Pinecone/Weaviate/Qdrant/Milvus documentation,
> retrieved 2026-06-08. Product versions and benchmark rankings change frequently — re-verify
> before committing to a stack.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution & seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- [`../scripts/search_eval.py`](../scripts/search_eval.py) — nDCG@k, MRR, recall@k, precision@k.
- Neighbour decision trees: `claude-app-engineering` (generation), `data-platform` (pipelines),
  `api-engineering` (API layer), `applied-statistics` (A/B significance).

_Last reviewed: 2026-06-08 by `claude`._
