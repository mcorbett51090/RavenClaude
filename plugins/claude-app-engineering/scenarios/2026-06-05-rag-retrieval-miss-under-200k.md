---
scenario_id: 2026-06-05-rag-retrieval-miss-under-200k
contributed_at: 2026-06-05
plugin: claude-app-engineering
product: rag
product_version: "unknown"
scope: likely-general
tags: [rag, retrieval, long-context, chunking, reranking, eval-the-retriever, contextual-retrieval]
confidence: medium
reviewed: false
---

## Problem

A "chat over our handbook" feature gave confidently wrong answers on a meaningful slice of questions — it would cite the wrong section, or answer from a plausible-but-irrelevant chunk and miss the section that actually held the answer. The team's instinct was that the *model* was hallucinating and that they needed a stronger model or more prompt engineering. The handbook was ~120K tokens total.

## Constraints context

- The whole corpus was ~120K tokens — comfortably under the ~200K threshold where holding it inline + caching the prefix is usually simpler, cheaper, and higher-recall than a retrieval pipeline `[verify-at-use]` against [`../knowledge/retrieval-and-rag-2026.md`](../knowledge/retrieval-and-rag-2026.md).
- They'd nonetheless built a RAG pipeline: naive fixed-size chunking (split every N chars), dense-only embedding retrieval, top-k = 3, no reranking, no contextual chunk prefixing.
- Failures were silent: the generator produced a fluent answer from whatever 3 chunks it got, so a *retrieval* miss looked like a *generation* (model) problem. There was no measurement separating the two.

## Attempts

- Tried: upgrading the generator to a more capable model. No meaningful change on the failing questions — the right chunk wasn't in the context to reason over, so a smarter reader couldn't recover it. This is the tell that the failure is upstream of the model.
- Tried: raising top-k from 3 to 15 to "catch more." Reduced misses slightly but bloated the context with low-relevance chunks and *added* distractor-driven wrong answers — quantity is not the lever; precision is.
- Tried (the diagnostic that reframed it): **evaluated the retriever separately from the generator** — built a small set of question→known-correct-chunk pairs and measured recall@k. Recall was the problem (the right chunk often wasn't in the top-k at all), which the end-to-end "answer looks wrong" signal had been hiding.
- Tried (the fix that worked, given the corpus size): for the ≤~200K corpus, the highest-leverage move was to **stop retrieving and hold the handbook inline above a cache breakpoint** — recall went to 100% (everything's in context), the cache made it cheap on repeat, and the wrong-section problem disappeared. Where a corpus genuinely must use RAG, the same diagnosis points at the pipeline fixes (below) instead.

## Resolution

**Diagnose retrieval and generation separately, and don't run RAG on a corpus that fits in context.** Two distinct lessons:

1. **A wrong answer over a corpus is a retrieval bug until proven otherwise.** Eval the retriever on its own (recall@k / MRR against question→correct-chunk pairs) *before* touching the generator or the prompt. A fluent wrong answer from the wrong chunk is indistinguishable from a model hallucination at the output layer — only separate measurement tells them apart.
2. **Under ~200K tokens, prefer long-context + caching over a pipeline** `[verify-at-use]`. A retrieval pipeline you didn't need is pure added failure surface (chunking, embedding, top-k, reranking — each a place to lose the right chunk). Skip it when the corpus fits; the "fine-tune-equivalent" outcome on Claude comes from better *context*, not a weight update or a pipeline.
3. **If RAG is genuinely required** (large/dynamic/per-tenant/citation-bearing corpus): naive fixed-size chunking + dense-only + no rerank is the weak default. The dated knowledge bank points at contextual chunk prefixing + hybrid (dense + BM25) + RRF + a reranking pass — and *keep* the retriever eval as the gate, since a pipeline change can drop recall while answers still look fine on the happy path.

The trap is the silent miss: the generator always produces *an* answer, so retrieval failures masquerade as model failures, and you spend effort on the wrong layer (bigger model, more prompt) while the right chunk never enters the context.

**Action for the next engineer:** when "the model is hallucinating over our docs," first ask "does the corpus even need RAG?" (size check) and "is the right chunk actually being retrieved?" (separate recall eval). Fix the layer the measurement points at — usually retrieval, often by removing the pipeline entirely.

Cross-reference: operationalizes [`../best-practices/rag-skip-it-under-200k.md`](../best-practices/rag-skip-it-under-200k.md), [`../best-practices/rag-retrieve-quality-over-quantity.md`](../best-practices/rag-retrieve-quality-over-quantity.md), and [`../best-practices/eval-the-retriever-separately.md`](../best-practices/eval-the-retriever-separately.md); see the retrieval-strategy decision tree in [`../knowledge/claude-app-decision-trees.md`](../knowledge/claude-app-decision-trees.md) and the new RAG-vs-long-context tree. The ~200K threshold + 1M window are dated — `[verify-at-use]` against the capability map.
