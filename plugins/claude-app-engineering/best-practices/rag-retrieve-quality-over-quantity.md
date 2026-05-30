# Retrieve for quality, not quantity — contextual chunks, hybrid search, then rerank

**Status:** Pattern — strong default; "retrieve top-50 and let the model sort it out" is the failure mode that quietly tanks answer quality.

**Domain:** Retrieval / context engineering

**Applies to:** `claude-app-engineering`

---

## Why this exists

Once you've decided RAG is warranted ([`rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md)), the instinct is to maximize *recall* — pull more chunks so the answer is "definitely in there." It backfires: a window stuffed with 50 loosely-relevant chunks dilutes attention, raises cost, and buries the one passage that mattered ("context rot"). What actually moves answer quality is **retrieval precision** — fewer, better chunks. Anthropic's **Contextual Retrieval** recipe is the 2026 default because it attacks precision at each stage: contextual embeddings (prepend a chunk-specific blurb so "the company" isn't ambiguous), contextual BM25 (exact-term recall), RRF fusion (semantics + exact terms), and a **reranker** — the single highest-ROI add — to keep only the top-K. The measured impact is large (contextual embeddings + BM25 cut top-20 retrieval failures ~49%; + reranking ~67% [verify-at-build]). The discipline: retrieve a wide candidate set, then **rerank down to a tight top-K** the model can actually use.

## How to apply

Contextualize chunks at ingest, run hybrid (dense + BM25) search, fuse with RRF, then rerank the top-N down to a small top-K. Pass the model the tight set with source metadata.

```python
# INGEST (once): prepend a chunk-specific context blurb, generated cheaply by caching the
# full doc as the prefix and asking Haiku for per-chunk context, THEN embed + BM25-index.
ctx = haiku_contextualize(full_doc_cached, chunk)          # ~50-100 tokens situating the chunk
embed(ctx + chunk); bm25_index(ctx + chunk)

# QUERY: hybrid retrieve wide -> fuse -> rerank narrow.
dense = vector_search(q, k=150)
lexical = bm25_search(q, k=150)
fused = reciprocal_rank_fusion(dense, lexical)             # semantics + exact terms
top_k = rerank(q, fused)[:20]                              # the highest-ROI step; keep ~20, not 150

# Generate over the TIGHT set, each chunk carrying source metadata for citations.
answer = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024,
    messages=[{"role": "user", "content": render(q, top_k)}])  # treat chunks as UNTRUSTED data
```

**Do:**
- **Contextualize chunks at ingest** — prepend a chunk-specific blurb (cache the full doc as the prefix; Haiku generates it cheaply) before embedding/indexing.
- Run **hybrid** search (dense + contextual BM25) and **fuse with RRF** — exact-term precision plus semantic recall.
- **Rerank** the wide candidate set down to a tight top-K (e.g. 150 → 20) — the single highest-ROI add after hybrid search.
- Return **source metadata** with each chunk for citations; treat every retrieved chunk as **untrusted** content (injection) ([`untrusted-content-stays-untrusted.md`](./untrusted-content-stays-untrusted.md)).

**Don't:**
- Maximize recall by jamming 50+ loosely-relevant chunks into the window — it dilutes attention, raises cost, and buries the signal.
- Ship dense-only retrieval and skip the reranker — you leave the largest quality gain on the table.
- Use fixed-size chunking blindly — prefer semantic/structural boundaries, modest overlap, ~200-800 tokens by content type.

## Edge cases / when the rule does NOT apply

- **`voyage-context-3`** encodes surrounding context at embed time, reducing the need for the manual contextual-embedding step — verify the model name and behavior before relying on it ([verify-at-build]).
- **Tiny / static corpus** — don't build this at all; hold it inline ([`rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md)).
- **Agentic RAG** — expose retrieval *as a tool* so the agent decides when to retrieve rather than always-prepending; the same precision discipline applies per call.
- The retrieval impact figures and embedding/rerank model names are **dated** — verify before quoting ([verify-at-build]).

## See also

- [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) — Contextual Retrieval, RRF, rerankers, Voyage embeddings, chunking, agentic RAG
- [`./rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md) — the decision that precedes building this pipeline
- [`./eval-the-retriever-separately.md`](./eval-the-retriever-separately.md) — proving the retriever's quality (recall@k, MRR) apart from the generator
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) · [`../agents/mcp-and-server-tools-engineer.md`](../agents/mcp-and-server-tools-engineer.md)

## Provenance

Codifies the Contextual Retrieval recipe from [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) (Anthropic Contextual Retrieval + cookbook, retrieved 2026-05-28). Impact percentages and embedding/rerank model names are dated — verify on the Researcher sweep before quoting a client.

---

_Last reviewed: 2026-05-30 by `claude`_
