# Evaluate retrieval separately from generation

**Status:** Absolute rule
**Domain:** RAG evaluation
**Applies to:** `search-relevance-engineering`

---

## Why this exists

In a RAG pipeline, retrieval failures and generation failures are orthogonal. A hallucinating
LLM and a retrieval system that misses the relevant chunk both produce bad answers, but they
require entirely different fixes. Conflating the two failures leads to the most expensive
diagnostic mistake in RAG engineering: improving the generation prompt (hard, slow, expensive)
when the root cause is that the retrieval stage never found the relevant document (easier to
measure, more tractable to fix).

The fix for retrieval is retrieval: better embeddings, better chunking, hybrid fusion,
reranking. The fix for generation is generation: better prompts, a better model, context
assembly changes. Applying a generation fix to a retrieval failure is wasted effort. Applying
a retrieval fix to a generation failure is also wasted effort. They must be diagnosed
separately.

## How to apply

- **Isolate the retrieval stage.** For every failing RAG query, first ask: "Is the relevant
  document or chunk in the top-k retrieved context?" If yes, the failure is generation-side.
  If no, the failure is retrieval-side.
- **Measure recall@k at the retrieval stage.** Without generating an answer, run the retrieval
  pipeline and measure whether the relevant chunk is in the top-k results. Use
  `scripts/search_eval.py` with your judgment set.
- **Set an explicit recall@k threshold.** Example: recall@20 ≥ 0.85 means "retrieval is good
  enough — investigate generation." Below the threshold, fix retrieval first.
- **Do not optimize prompts to compensate for retrieval failure.** A prompt that says "if you
  can't find the answer, say I don't know" does not fix a missing chunk in the context.

**Do:**

- Maintain a retrieval-evaluation harness separate from end-to-end RAG evaluation.
- Report recall@k alongside end-to-end answer quality metrics in every evaluation run.
- When a new RAG failure is reported, run the retrieval recall check before touching the
  generation side.

**Don't:**

- Evaluate RAG quality only end-to-end (e.g. LLM-as-judge on the final answer) without
  isolating the retrieval stage.
- Improve context window size as a retrieval fix — stuffing more chunks does not raise
  recall if the relevant chunk was outside the top-k.
- Attribute a hallucination to the LLM without first verifying that the relevant ground-truth
  was in the retrieved context.

## Edge cases / when the rule does NOT apply

- A system where the LLM is doing closed-book answering (no retrieval) — obviously only
  generation quality matters.
- A RAG system where the answer is always fully contained in a single top-1 retrieved chunk
  and recall@1 is reliably ≥ 0.99. Even here, monitoring recall@1 as the retrieval health
  signal is still recommended.

## See also

- [`./measure-relevance-with-judgments-not-vibes.md`](./measure-relevance-with-judgments-not-vibes.md) — how to measure retrieval quality.
- [`../agents/search-eval-engineer.md`](../agents/search-eval-engineer.md) — the agent who runs the retrieval isolation evaluation.
- [`../skills/retrieval-evaluation/SKILL.md`](../skills/retrieval-evaluation/SKILL.md) — the evaluation playbook.
- Seam: `claude-app-engineering` — owns the generation layer once retrieval checks out.

## Provenance

The retrieval-vs-generation failure attribution discipline is documented in Anthropic's RAG
guidance and in the LangChain / LlamaIndex RAG evaluation documentation (2023–2024). The
RAGAS framework (Es et al., 2023) formalizes the separation into context precision/recall
(retrieval) and answer faithfulness/relevance (generation). The principle is first-principles
diagnostic discipline: fix the upstream failure mode before the downstream one. [verify-at-use
for current RAGAS version and API]

---

_Last reviewed: 2026-06-08 by `claude`._
