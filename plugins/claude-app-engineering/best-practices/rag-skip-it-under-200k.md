# Skip RAG under ~200K tokens — long context + caching first

**Status:** Pattern — strong default; building a retrieval pipeline for a corpus that fits in context is needless complexity.

**Domain:** Retrieval / context engineering

**Applies to:** `claude-app-engineering`

---

## Why this exists

RAG is a real engineering investment — chunking, an embedding model, a vector store, hybrid search, a reranker, an ingestion pipeline, and its own eval surface. Teams reach for it reflexively the moment "answer over documents" appears, and pay that complexity tax even when the corpus is small and static enough to simply put in the prompt. With a 1M-token window (Opus 4.7 / Sonnet 4.6 [verify-at-build]) and prompt caching at 0.1× read, holding a corpus **under ~200K tokens** [verify-at-build] inline is usually faster, simpler, *and* cheaper than retrieving over it — the whole corpus sits above a cache breakpoint and every request after the first reads it at a tenth of input cost. The first retrieval decision is therefore not "which vector DB" but **"do I even need retrieval"** — and under the threshold, with a reasonably static corpus, the answer is no.

## How to apply

Size the corpus first. Under the threshold and static → hold it inline above a cache breakpoint. Large / dynamic / per-tenant / must-cite → then build retrieval.

```python
# Corpus fits + static -> hold it, cache it, ask the question last.
system = [
    {"type": "text", "text": ROLE_AND_RULES},
    {"type": "text", "text": WHOLE_CORPUS,                 # < ~200K tokens, fairly static
     "cache_control": {"type": "ephemeral"}},               # cached: every later read is 0.1x
]
messages = [{"role": "user", "content": f"<question>{q}</question>"}]  # question LAST

# Only cross into a pipeline when an observable pushes you there:
#   corpus large / dynamic / per-user / must surface citations -> Files API or Contextual Retrieval
```

**Do:**
- **Estimate the corpus size first.** Under ~200K tokens [verify-at-build] and reasonably static → hold it inline and cache the prefix; the curation overhead of RAG isn't worth it.
- Put the corpus **first / above the breakpoint**, the question **last** — cacheable and better-recalled ([`context-budget-the-1m-window.md`](./context-budget-the-1m-window.md)).
- Use the **Files API** when it's a known small set of documents per request (upload once, reference by id) — between "hold inline" and "full RAG" ([`../knowledge/server-side-tools-and-files.md`](../knowledge/server-side-tools-and-files.md)).
- Cross into a **retrieval pipeline** only on an observable signal: the corpus is large, dynamic, per-tenant, or you must surface citations.

**Don't:**
- Build a vector store + reranker for a 50-page handbook that fits in one cached prefix.
- Conversely, stuff a huge or per-request-changing corpus inline "to skip RAG" — past the threshold you pay full input every call and dilute attention ([`context-budget-the-1m-window.md`](./context-budget-the-1m-window.md)).
- Quote the ~200K boundary or the window size as fixed — both are dated; verify against the capability map ([verify-at-build]).

## Edge cases / when the rule does NOT apply

- **Dynamic / per-tenant / frequently-updated** corpora don't cache well and may exceed the window even when "small per query" — retrieve ([`rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md)).
- **Citation requirements** can push you to retrieval even under the threshold, to attribute spans to sources cleanly.
- **Latency-sensitive** paths: a 180K-token cached prefix still has a real prefill cost on a cache *miss* — pre-warm it, or retrieve a slice if first-token latency is the binding constraint.
- The threshold is **dated** — re-verify the window size and the ~200K boundary before designing around them.

## Edge cases note

When you *do* retrieve, quality beats quantity — see [`rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md).

## See also

- [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) — the do-you-even-need-RAG tree, Files API, Contextual Retrieval
- [`./context-budget-the-1m-window.md`](./context-budget-the-1m-window.md) — the retrieve-vs-hold budget the threshold lives inside
- [`./cache-the-static-prefix.md`](./cache-the-static-prefix.md) — caching is what makes "hold it inline" cheap
- [`../agents/prompt-and-context-engineer.md`](../agents/prompt-and-context-engineer.md) — owns the retrieve-vs-hold decision

## Provenance

Codifies the "do you even need RAG?" decision from [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) (Anthropic Contextual Retrieval + cookbook, retrieved 2026-05-28) and the retrieve-vs-hold lever in [`../knowledge/context-engineering-2026.md`](../knowledge/context-engineering-2026.md). The ~200K threshold and 1M window are dated — verify against [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md).

---

_Last reviewed: 2026-05-30 by `claude`_
