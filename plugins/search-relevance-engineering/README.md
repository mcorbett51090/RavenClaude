# search-relevance-engineering

The **search and retrieval layer** — from index design through query understanding, relevance
tuning, vector/hybrid retrieval, and offline/online evaluation. This plugin's team fills the gap
that `claude-app-engineering` only touches at the app surface, owning everything from the
retrieval topology down to the nDCG score that proves it works.

> **The one-line philosophy:** measure before you tune, hybrid almost always beats pure-vector,
> chunk for the question not the document, and evaluate retrieval separately from generation.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Should we use Elasticsearch, Pinecone, or pgvector? Design our search stack." | **search-relevance-engineering** (`search-architect`) |
| "Our search results are irrelevant — tune BM25, synonyms, analyzers, LTR." | **search-relevance-engineering** (`relevance-engineer`) |
| "Build semantic search, choose an embedding model, design chunking, add a reranker." | **search-relevance-engineering** (`vector-retrieval-engineer`) |
| "Measure search quality — nDCG, MRR, A/B test a ranking change, build judgment sets." | **search-relevance-engineering** (`search-eval-engineer`) |
| "Build the RAG prompt / generation chain on top of retrieved context." | `claude-app-engineering` |
| "Build the embedding ingestion pipeline / batch embedding job." | `data-platform` / `ml-engineering` |
| "Design the API contract in front of search." | `api-engineering` |
| "Run A/B significance tests on ranking changes." | `applied-statistics` |

## What's inside

- **4 agents** — `search-architect`, `relevance-engineer`, `vector-retrieval-engineer`,
  `search-eval-engineer`.
- **3 skills** — `lexical-vector-hybrid-retrieval`, `relevance-tuning`, `retrieval-evaluation`.
- **3 commands** — `/search-relevance-engineering:design-search-architecture`,
  `:tune-relevance`, `:build-relevance-judgments`.
- **2 templates** — `relevance-judgment-set.md`, `index-mapping-spec.md`.
- **Knowledge bank** — `knowledge/search-retrieval-decision-trees.md`: Mermaid trees for
  lexical-vs-vector-vs-hybrid, chunking strategy, and rerank-or-not, plus a dated 2026
  capability map.
- **6 best-practices** and **1 advisory hook** (flags vector-only designs, hardcoded chunk
  sizes, relevance claims without metrics, rerankers without recall/latency notes).
- **`scripts/search_eval.py`** — stdlib-only nDCG@k, MRR, recall@k, precision@k calculator
  with self-test.

## House opinions (the short list)

1. Measure before you tune — baseline nDCG/MRR first, then change one thing.
2. Hybrid almost always beats pure-vector for real corpora.
3. Chunk for the question, not the document.
4. An embedding model is a choice — benchmark on your corpus.
5. Evaluate retrieval separately from generation.
6. Rerank when recall is cheap and precision is expensive.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
