# Hybrid almost always beats pure-vector for most real corpora

**Status:** Pattern
**Domain:** Retrieval strategy
**Applies to:** `search-relevance-engineering`

---

## Why this exists

Dense vector retrieval is powerful for semantic similarity but structurally blind to exact-match
signals. A bi-encoder embedding a query like "SKU-9284-X" produces a vector similar to
documents about similar-sounding products — not the one with that exact code. Product catalogues,
technical documentation, legal databases, and code search all have a mix of exact-match and
semantic queries. Pure-vector retrieval fails the exact-match fraction silently: users never see
the exact document because it wasn't in the top-k, and the failure is invisible unless measured.

BM25 by contrast excels at exact-match, rare terms, abbreviations, and out-of-vocabulary words.
Hybrid fusion (BM25 + dense + RRF) captures both: BM25 handles what embeddings miss; dense
handles what token-overlap misses. In practice, RRF hybrid consistently outperforms either
single mode on mixed corpora in BEIR and enterprise benchmarks.

## How to apply

- Default to hybrid (BM25 + dense + RRF) for any corpus that has product codes, identifiers,
  proper nouns, abbreviations, or acronyms in the query mix.
- Run corpus analysis before committing to pure-vector: what fraction of unique queries in the
  last 30 days contain tokens with high TF-IDF weight but no semantic near-neighbours?
- Measure both retrieval modes against a judgment set. Hybrid nDCG@10 should be ≥ either
  single-mode alone on a mixed corpus.

**Do:**

- Start with RRF(k=60) as the fusion default — it is parameter-light and empirically robust.
- Verify pure-vector recall on tail queries; exact-match failures concentrate in the tail.
- Keep BM25 scoring alongside dense vectors even in primarily semantic use cases.

**Don't:**

- Choose pure-vector because the vendor demo was impressive without testing on your corpus.
- Assume that a better embedding model will fix an exact-match failure — it structurally cannot.
- Remove the lexical path from a hybrid pipeline to reduce complexity without measuring the
  nDCG regression.

## Edge cases / when the rule does NOT apply

- A corpus of purely conceptual documents with no proper nouns, codes, or abbreviations —
  e.g. a philosophical essay corpus where all queries are paraphrase-style. Even here,
  measuring pure-vector vs hybrid on a judgment set before deciding is still recommended.
- A system where the query interface enforces structured, code-only lookups (e.g. an internal
  asset lookup by exact asset ID). In this case pure-lexical (keyword) is sufficient.

## See also

- [`./measure-relevance-with-judgments-not-vibes.md`](./measure-relevance-with-judgments-not-vibes.md) — verify the claim with nDCG.
- [`../knowledge/search-retrieval-decision-trees.md`](../knowledge/search-retrieval-decision-trees.md) — the Lexical vs Vector vs Hybrid tree.
- [`../skills/lexical-vector-hybrid-retrieval/SKILL.md`](../skills/lexical-vector-hybrid-retrieval/SKILL.md) — implementation playbook.

## Provenance

Grounded in BEIR benchmark results (Thakur et al., 2021) showing hybrid retrieval consistently
outperforms single-mode on out-of-domain benchmarks, and in Elasticsearch/Weaviate published
evaluations of RRF hybrid on mixed corpora. First-principles: BM25 and dense vectors are
complementary, not competing, models of relevance. [verify-at-use for current benchmark numbers]

---

_Last reviewed: 2026-06-08 by `claude`._
