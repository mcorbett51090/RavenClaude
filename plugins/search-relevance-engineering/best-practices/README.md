# search-relevance-engineering — best-practice docs

Named, citable rules for the `search-relevance-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_6 rules._

| Doc | Status | Use when |
|---|---|---|
| [`hybrid-beats-pure-vector-for-most-corpora.md`](./hybrid-beats-pure-vector-for-most-corpora.md) | Pattern | Choosing a retrieval strategy for any mixed corpus |
| [`measure-relevance-with-judgments-not-vibes.md`](./measure-relevance-with-judgments-not-vibes.md) | Absolute rule | Before any tuning cycle, and before declaring a change "better" |
| [`chunk-for-the-question-not-the-document.md`](./chunk-for-the-question-not-the-document.md) | Pattern | Designing or reviewing a chunking strategy for RAG or semantic search |
| [`rerank-when-recall-is-cheap-and-precision-is-not.md`](./rerank-when-recall-is-cheap-and-precision-is-not.md) | Pattern | Deciding whether to add a cross-encoder reranker to a retrieval pipeline |
| [`an-embedding-model-is-a-choice-not-a-default.md`](./an-embedding-model-is-a-choice-not-a-default.md) | Pattern | Selecting an embedding model for any search or RAG pipeline |
| [`evaluate-retrieval-separately-from-generation.md`](./evaluate-retrieval-separately-from-generation.md) | Absolute rule | Debugging a RAG pipeline or attributing quality failures |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../knowledge/search-retrieval-decision-trees.md`](../knowledge/search-retrieval-decision-trees.md) — decision trees + 2026 capability map.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
