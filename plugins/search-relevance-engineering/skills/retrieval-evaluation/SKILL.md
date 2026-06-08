---
description: "Build relevance judgment sets and compute offline evaluation metrics (nDCG@k, MRR, recall@k, precision@k) for a search or RAG retrieval system. Produces a reproducible evaluation harness and a baseline metric report."
---

# Retrieval Evaluation

**Purpose:** establish a reproducible measurement baseline for a search or RAG retrieval
system — from judgment-set construction through metric computation — so that every subsequent
tuning change has a trustworthy before/after comparison.

---

## Operating loop

### Part A — Judgment-set construction

1. **Query sampling.** Sample across the query distribution:
   - Head (top 10% by frequency): high volume, often navigational or branded.
   - Torso (10th–80th percentile): informational queries with multiple relevant docs.
   - Tail (bottom 20%): rare queries, often where worst failures hide.
   Minimum: 100 total queries for a meaningful nDCG@10 comparison; 300+ for LTR training.

2. **Annotation scale.** Use the NIST 4-point scale:
   - 0 = not relevant
   - 1 = marginally relevant
   - 2 = relevant
   - 3 = highly relevant (the ideal result)
   Binary (0/1) is acceptable for recall@k in RAG pipelines.

3. **Annotation guidelines.** Write a one-page guideline per query type with:
   - What makes a document relevant for this query type?
   - How to score partial relevance?
   - Two worked examples per relevance grade?

4. **Inter-annotator agreement.** Get at least two independent annotators for a random 20%
   sample. Target Cohen's kappa ≥ 0.6. Below 0.4 means the guidelines are underspecified —
   fix the guidelines before continuing.

5. **Judgment-set format.** Store as a structured list:
   `[{ query_id, query_text, doc_id, relevance_grade }, ...]`
   Use `templates/relevance-judgment-set.md` as the working template.

---

### Part B — Metric computation

6. **nDCG@k** (Normalized Discounted Cumulative Gain).
   `DCG@k = Σ (2^rel_i - 1) / log2(i+1)` for i=1..k;
   `nDCG@k = DCG@k / IDCG@k` (IDCG = ideal DCG with perfect ranking).
   Use k=10 for web-style search; k=5 for navigational; k=20–100 for RAG recall.

7. **MRR** (Mean Reciprocal Rank).
   `MRR = (1/|Q|) Σ 1/rank_i` where rank_i is the rank of the first relevant result.
   Best when there is typically one correct answer (e.g. FAQ, factual lookup).

8. **recall@k.**
   `recall@k = (relevant docs in top-k) / (total relevant docs)`.
   Primary RAG metric — "was the relevant chunk in the context window?"

9. **precision@k.**
   `precision@k = (relevant docs in top-k) / k`.
   Useful for measuring hallucination risk in RAG (too many irrelevant chunks in context).

10. **Run the calculator.** Use `scripts/search_eval.py`:
    ```
    python3 scripts/search_eval.py
    ```
    The script accepts a judgment list and ranked result lists; prints nDCG@k, MRR,
    recall@k, precision@k. See `__main__` section for the input format.

---

### Part C — Baseline report

11. **Document the baseline.** Record:
    - judgment set version + date + annotator count + kappa
    - retrieval system version (index name, query body, model)
    - nDCG@10, MRR, recall@k (k=100 for RAG), precision@10
    - worst-10 queries by nDCG (for `relevance-engineer` error analysis)

12. **Threshold interpretation guide.**
    | nDCG@10 | Rough interpretation |
    |---|---|
    | < 0.4 | Poor — major relevance problems |
    | 0.4 – 0.6 | Mediocre — tuning will help |
    | 0.6 – 0.75 | Reasonable — incremental improvements possible |
    | > 0.75 | Strong — diminishing returns |
    These are rough guides; absolute values depend heavily on query difficulty and corpus size.

---

## Anti-patterns

- Building a judgment set from head queries only — tail queries reveal the worst failures.
- Measuring nDCG without checking inter-annotator agreement — disagreeing annotators produce
  untrustworthy nDCG scores.
- Using CTR as a proxy for nDCG — click-through measures attention, not relevance.
- Changing the system and the judgment set simultaneously — the delta is uninterpretable.

---

## Output

A judgment set (use `templates/relevance-judgment-set.md`) + a baseline metric report
(nDCG@k, MRR, recall@k, precision@k with interpretation) + a worst-10-query list for the
tuning team + a handoff note for `relevance-engineer` or `vector-retrieval-engineer`.
