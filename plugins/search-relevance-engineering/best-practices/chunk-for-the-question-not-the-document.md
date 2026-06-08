# Chunk for the question, not the document

**Status:** Pattern
**Domain:** Chunking strategy
**Applies to:** `search-relevance-engineering`

---

## Why this exists

A chunk boundary should maximize the probability that a retrieved chunk contains a complete,
self-contained answer to the expected query — not that it respects the document's internal
structure. Document structure (chapters, sections, paragraphs) and answer structure (the thing
a user needs) are different things. A 4096-token page chunk that contains a relevant paragraph
among 3900 tokens of irrelevant context hurts precision. A 50-token chunk that splits a
sentence in the middle of the key fact hurts recall.

The most common failure is cargo-culting a "512 tokens" default from a tutorial without
measuring whether that chunk size works for the specific corpus and query distribution. Chunk
size is a data-driven parameter, not a constant.

## How to apply

- Identify the **question shape** first: are queries short factual lookups? Multi-sentence
  conceptual questions? Code function lookups? The answer shape determines the ideal chunk.
- For structured documents (headers, sections): try section-header chunking first — each
  section is a candidate chunk. Sections are often naturally sized for answers.
- For long prose documents: use fixed-stride with overlap (e.g. 256–512 tokens, 10–20%
  overlap to preserve context at boundaries). Measure recall@k at 128, 256, and 512 tokens.
- For very long documents where the query targets a sub-section: use parent-child chunking —
  embed small chunks (128–256 tokens) for precision retrieval; return the parent context
  window (1024–2048 tokens) for LLM answer quality.
- **Measure.** Run recall@k and precision@k at multiple chunk sizes on a sample of ≥ 50 real
  queries. Pick the size that maximises the combined recall + precision on your query
  distribution.

**Do:**

- Document the chunk size rationale: why this size, measured how.
- Use overlap (10–20%) at chunk boundaries to prevent answer splits.
- Re-measure recall@k when the corpus or query distribution changes significantly.

**Don't:**

- Hardcode 512 tokens without measuring.
- Use the same chunk size for a code corpus and a prose corpus.
- Optimize chunk size only on head queries — tail queries often have the worst chunk-boundary
  failures.

## Edge cases / when the rule does NOT apply

- Short documents (< 512 tokens): embed the whole document as a single chunk.
- Structured data (tables, JSON records, database rows): each record or row is the natural
  unit; token-count chunking is wrong.
- A system where the retrieval context is always summarised by the LLM (map-reduce RAG): the
  chunk/precision tradeoff changes because precision is less critical when every retrieved
  chunk gets a summary pass.

## See also

- [`./evaluate-retrieval-separately-from-generation.md`](./evaluate-retrieval-separately-from-generation.md)
- [`../knowledge/search-retrieval-decision-trees.md`](../knowledge/search-retrieval-decision-trees.md) — the Chunking Strategy tree.
- [`../agents/vector-retrieval-engineer.md`](../agents/vector-retrieval-engineer.md) — chunking design owner.

## Provenance

Parent-child chunking popularized by LangChain/LlamaIndex documentation and Anthropic's RAG
guidance (2023–2024); the recall vs precision tradeoff with chunk size is documented in
Pinecone and Weaviate retrieval benchmarks and community benchmarks (2024). The general
principle — optimize for the answer shape, not the document shape — is first-principles
information retrieval. [verify-at-use for specific benchmark citations]

---

_Last reviewed: 2026-06-08 by `claude`._
