---
description: "Tune a lexical or hybrid search system's relevance: BM25 parameter sweep (k1, b), field-level boosting, custom analyzer design, synonym/antonym handling, query rewriting, and learning-to-rank setup. Requires a judgment set and baseline metric as inputs."
---

# Relevance Tuning

**Purpose:** take a search system with a baseline nDCG@k/MRR metric and a judgment set, and
apply a structured sequence of relevance improvements — from cheap BM25 parameter sweeps
through field-boost optimization to learning-to-rank — returning before/after metric deltas
and rollout-ready configuration changes.

---

## Prerequisites

- A judgment set of ≥ 100 query–document pairs with graded relevance (0–3 scale). If absent,
  run the `retrieval-evaluation` skill first.
- A baseline nDCG@10 and MRR score against that judgment set.
- Index access (read mapping, run test queries) or a documented index mapping.

---

## Operating loop

### Phase 1 — Diagnostic

1. **Error analysis on the bottom quartile.** For the 25% of queries with the lowest nDCG@k,
   classify the failure mode: wrong tokenization, missing synonyms, wrong field weight, or
   semantic gap (cannot be fixed lexically — escalate to `vector-retrieval-engineer`).
2. **BM25 parameter sense-check.** Default Elasticsearch BM25: k1=1.2, b=0.75. Check if these
   are even correct for the index similarity setting (`BM25` vs `classic` TF-IDF).

### Phase 2 — BM25 parameter sweep

3. **k1 sweep** (0.5, 0.75, 1.0, 1.2, 1.5, 2.0) — controls term-frequency saturation.
   Lower k1 reduces the effect of repeated terms; higher amplifies it. Short-document corpora
   often prefer k1 ≤ 1.0.
4. **b sweep** (0.0, 0.25, 0.5, 0.75, 1.0) — controls field-length normalization.
   b=0 disables normalization; b=1 fully penalises long documents. Use held-out 20% of
   judgment set to pick parameters that maximise nDCG@10.

### Phase 3 — Field-level boosting

5. **BM25F multi-field boost matrix.** Set per-field boosts: title × 3–5, body × 1,
   tags/metadata × 2–4 (domain-specific). Use `multi_match type: best_fields` with
   `tie_breaker: 0.3` as a starting point; measure nDCG@10 before and after.

### Phase 4 — Analyzer design

6. **Tokenization audit.** Run `_analyze` API on representative queries and documents.
   Check for: over-stemming (losing meaning), under-stemming (missing morphological variants),
   missing ASCII-folding (accent handling), n-gram gaps (prefix search).
7. **Synonym graph filter.** Build expansion synonyms at query-time (not index-time) to avoid
   index explosion. Multi-word synonyms require the `synonym_graph` filter at query time only.
   Review list quarterly — stale synonyms create false positives.
8. **Re-index plan.** If an analyzer change is needed: create a new index with the updated
   mapping, reindex documents, cut over via alias. Never change an analyzer in-place on
   an existing index with live traffic.

### Phase 5 — Learning-to-rank (only when BM25 + boosts saturate)

9. **Feature set.** BM25 score (base), per-field BM25 scores (title, body), query-document
   freshness, popularity (click rate). Keep the feature count ≤ 20 for interpretability.
10. **Training data.** Build from click logs (implicit feedback, biased toward position)
    or from the judgment set (explicit, unbiased). Debias click data with IPS weighting.
11. **Model.** LambdaMART (Elasticsearch LTR plugin, XGBoost) for list-wise ranking.
    Neural LTR only when LambdaMART saturates and training data is large (≥ 10k query-doc pairs).
12. **A/B.** Offline nDCG gate first (must beat baseline), then online A/B via
    `search-eval-engineer`.

---

## Anti-patterns

- Declaring a tuning improvement without before/after nDCG numbers.
- Changing the analyzer without planning the re-index.
- Jumping to LTR without exhausting BM25 + field-boost tuning.
- Synonyms at index-time for multi-word phrases (causes token graph corruption).

---

## Output

A configuration change set (index settings diff + query body diff) with before/after nDCG@k
and MRR, a re-index plan if the analyzer changed, and a measurement plan for the next round.
