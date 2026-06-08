---
description: "Compute NDCG, MRR, and precision@k against the judgment list with a baseline. Reach for this before any tuning."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Measure relevance

You are running `/search-relevance-engineering:measure-relevance` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Load the judgment list — Graded relevance labels for a representative query set (§3 #3).
2. Compute NDCG — DCG = Σ rel_i / log2(i+1) (rank i from 1); NDCG = DCG/IDCG via `search_relevance_engineering_calc.py relevance` (§3 #1).
3. Compute MRR + precision@k — MRR for first-relevant; precision@k for top-k quality (§3 #1).
4. Baseline before tuning — Record the baseline; every change reports a before/after delta (§3 #1 #3).

## Output
An NDCG/MRR/precision@k read against the judgment list with a baseline. Traverse Tree 1 in the decision-trees file. See [`../skills/measure-relevance/SKILL.md`](../skills/measure-relevance/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No query/user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
