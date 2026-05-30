# Eval the retriever apart from the generator — recall@k and MRR, not just answer quality

**Status:** Primary diagnostic — when a RAG answer is wrong, check retrieval before you touch the prompt.

**Domain:** Evals / retrieval

**Applies to:** `claude-app-engineering`

---

## Why this exists

In a RAG app, a wrong answer has two very different root causes: the right chunk was never retrieved (a retrieval failure) or the right chunk was retrieved and the model misused it (a generation failure). If your only metric is end-to-end answer quality, you can't tell them apart — and you'll waste cycles rewriting the prompt when the fix was the chunking or the reranker, or vice versa. Evaluating the **retriever separately** (recall@k, MRR over a labelled query→relevant-chunk set) localizes the failure: a low recall@k says the answer was never reachable, so no prompt change will save it. This is the diagnostic that turns "the RAG is bad" into a specific, fixable component — and it's the gate that keeps a retrieval-pipeline change ([`rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md)) honest the same way [`evals-before-vibes.md`](./evals-before-vibes.md) gates a prompt change.

## How to apply

Build a labelled set of queries with their known-relevant chunk ids; score retrieval with recall@k + MRR independently of the generator; gate retrieval changes on that delta.

```python
# Labelled set: query -> the chunk id(s) that actually answer it.
GOLD = [{"q": "What's the refund window?", "relevant": {"chunk_4f2"}}, ...]

def eval_retriever(retrieve, k=20):
    hits = mrr_sum = 0
    for case in GOLD:
        ranked = [c.id for c in retrieve(case["q"], k)]
        if case["relevant"] & set(ranked):
            hits += 1
            rank = next(i for i, cid in enumerate(ranked, 1) if cid in case["relevant"])
            mrr_sum += 1 / rank                       # earlier-ranked relevant chunk scores higher
    return {"recall@k": hits / len(GOLD), "mrr": mrr_sum / len(GOLD)}

# Localize the failure: low recall@k -> fix retrieval (chunking/rerank); high recall@k but
# wrong answers -> fix generation (the prompt/model). Gate pipeline changes on the retriever delta.
assert eval_retriever(candidate)["recall@k"] >= baseline_recall - THRESHOLD
```

**Do:**
- Maintain a **labelled query→relevant-chunk** set and score **recall@k + MRR** for retrieval on its own, before measuring end-to-end answer quality.
- Use the split to **localize**: low recall@k → fix retrieval (chunking, hybrid search, reranker); high recall@k but bad answers → fix the prompt/model.
- **Gate retrieval-pipeline changes** (new chunker, new embedding model, added reranker) on the retriever delta — a "better" pipeline that drops recall@k is a regression.
- Grow the labelled set from **production retrieval misses**, the same way the answer golden set grows from answer failures ([`evals-before-vibes.md`](./evals-before-vibes.md)).

**Don't:**
- Rewrite the generation prompt to fix an answer whose relevant chunk was never retrieved — no prompt change reaches a chunk that isn't in the window.
- Ship a retrieval change because answers "look better" end-to-end — measure recall@k/MRR, the named [`evals-before-vibes.md`](./evals-before-vibes.md) discipline applied to the retriever.
- Conflate the retriever metric with the answer metric — they move independently and diagnose different bugs.

## Edge cases / when the rule does NOT apply

- **Non-RAG apps** have no retriever to evaluate — this is the RAG-specific complement to [`evals-before-vibes.md`](./evals-before-vibes.md).
- **Long-context (no retrieval)** apps skip this entirely — there's no retrieval step to isolate ([`rag-skip-it-under-200k.md`](./rag-skip-it-under-200k.md)).
- **Generation-only regressions** still go through the answer golden set + LLM-judge discipline — this rule adds the retriever gate, it doesn't replace the answer eval.
- A relevant chunk **retrieved but reranked out of the top-K** is a retriever failure at *that K* — evaluate recall@k at the K you actually pass to the model, not an inflated candidate K.

## See also

- [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) — "eval the retriever separately from the generator (recall@k, MRR)"
- [`../knowledge/evals-and-quality.md`](../knowledge/evals-and-quality.md) — the golden-set + grader discipline this extends
- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the answer-side gate this complements
- [`./rag-retrieve-quality-over-quantity.md`](./rag-retrieve-quality-over-quantity.md) — the pipeline this metric gates; [`../agents/eval-engineer.md`](../agents/eval-engineer.md) owns it

## Provenance

Codifies "eval the retriever separately from the generator (recall@k, MRR)" from [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md) (Anthropic RAG guidance + cookbook, retrieved 2026-05-28), composed with the golden-set discipline in [`../knowledge/evals-and-quality.md`](../knowledge/evals-and-quality.md).

---

_Last reviewed: 2026-05-30 by `claude`_
