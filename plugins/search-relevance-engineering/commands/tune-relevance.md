---
description: "Given a baseline nDCG@k score and a judgment set, run a structured relevance tuning cycle: BM25 parameter sweep, field-boost optimization, analyzer/synonym changes, and optionally LTR setup. Outputs configuration diffs with before/after metrics."
argument-hint: "[context, e.g. 'Elasticsearch 8.x, baseline nDCG@10=0.52, MRR=0.61, 250 judgment queries, title+body+tags fields, 80% precision complaints']"
---

You are running `/search-relevance-engineering:tune-relevance`. Use the `relevance-engineer`
discipline and the `relevance-tuning` skill.

## Steps

1. **Confirm prerequisites.** A judgment set and baseline nDCG@k are required. If absent,
   pause and spawn `search-eval-engineer` first (via the Team Lead) to establish a baseline.

2. **Error analysis.** Identify the bottom-quartile queries by nDCG score. Classify each
   failure mode: tokenization error, missing synonym, wrong field weight, or semantic gap
   (semantic gaps route to `vector-retrieval-engineer`, not here).

3. **BM25 parameter sweep.** Propose a k1 × b grid (k1: 0.5, 0.75, 1.0, 1.2, 1.5, 2.0;
   b: 0.0, 0.25, 0.5, 0.75, 1.0). Identify the grid point that maximises nDCG@10 on the
   held-out 20% of the judgment set. Output the winning parameters with the nDCG delta.

4. **Field-boost optimization.** Propose a per-field boost matrix. Measure nDCG@10 with
   the winning boosts. Output the `multi_match` query change.

5. **Analyzer audit (if needed).** Run `_analyze` on representative queries and documents.
   If tokenization failures explain ≥ 10% of the bottom quartile, propose a custom analyzer
   and a re-index plan. Never change the analyzer without a re-index plan.

6. **Synonym/query-rewriting changes.** If synonym gaps explain failures, propose the
   synonym-graph filter config. Confirm expansion direction (query-time only, not index-time
   for multi-word synonyms).

7. **LTR (only if phases 3–6 do not close the gap).** Propose a feature set, a training-data
   construction plan, and an offline nDCG gate before any A/B.

8. **Rollout plan.** Stage the changes: parameter change (zero-downtime) → analyzer change
   (requires re-index) → LTR (shadow mode before full swap). Each stage requires an nDCG@k
   check before proceeding to the next.

9. Follow the Structured Output Protocol (`ravenclaude-core`) at the end.
