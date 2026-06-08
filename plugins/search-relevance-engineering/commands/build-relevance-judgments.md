---
description: "Build a relevance judgment set from scratch: sample queries across head/torso/tail distribution, write annotation guidelines with a 4-point relevance scale, compute inter-annotator agreement, and produce a baseline nDCG@10, MRR, and recall@k report."
argument-hint: "[context, e.g. 'e-commerce search, ~5k daily queries, top-1000 queries available, two internal annotators, Elasticsearch BM25 current system']"
---

You are running `/search-relevance-engineering:build-relevance-judgments`. Use the
`search-eval-engineer` discipline and the `retrieval-evaluation` skill.

## Steps

1. **Query sampling plan.** From the argument or by asking: total distinct queries, available
   query log, frequency distribution. Propose:
   - Head stratum: top-10% by frequency (navigational, branded — easy to judge).
   - Torso: 10th–80th percentile (informational — most relevant for nDCG).
   - Tail: random sample from bottom 20% (rare failures, often worst quality).
   Minimum 100 total; recommend 250 for meaningful nDCG@10 comparisons.

2. **Annotation guidelines.** Write a one-page guideline covering:
   - The 4-point relevance scale (0=not relevant, 1=marginally, 2=relevant, 3=highly relevant).
   - What counts as relevant for this specific domain (2 worked examples per grade).
   - Edge-case rules (partial matches, outdated content, language mismatches).
   - A "when in doubt, score 1" tie-break rule.

3. **Pooling.** For each sampled query, pool candidates: top-20 results from the current
   system + top-20 from at least one alternative retrieval mode. Annotators score only the
   pooled set (not all documents), so pool depth matters for recall estimation.

4. **Inter-annotator agreement.** Identify the random 20% overlap sample. After annotation,
   compute Cohen's kappa. Report the result:
   - kappa ≥ 0.6: proceed.
   - 0.4 ≤ kappa < 0.6: review disagreement cases, refine guidelines, re-annotate the
     disagreement set.
   - kappa < 0.4: guidelines are broken — stop, fix, restart.

5. **Judgment set format.** Produce the final set using `templates/relevance-judgment-set.md`.
   Include: query_id, query_text, doc_id, doc_title, relevance_grade, annotator, date.

6. **Baseline metric computation.** Run `scripts/search_eval.py` on the pooled results.
   Report nDCG@10, MRR, recall@k (k=20 for search; k=100 for RAG), precision@10.
   Include the worst-10-query list with their nDCG scores.

7. **Handoffs.** Emit the baseline report to `relevance-engineer` (BM25 tuning) and/or
   `vector-retrieval-engineer` (semantic gaps) as appropriate.

8. Follow the Structured Output Protocol (`ravenclaude-core`) at the end.
