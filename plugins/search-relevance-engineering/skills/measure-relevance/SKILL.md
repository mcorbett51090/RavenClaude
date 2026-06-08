---
name: measure-relevance
description: "Compute NDCG, MRR, and precision@k against the judgment list with a baseline. Reach for this before any tuning."
---

# Skill: Measure relevance

'These results look better' is one session, not a metric (§3 #1).

## Step 1 — Load the judgment list
Graded relevance labels for a representative query set (§3 #3).

## Step 2 — Compute NDCG
DCG = Σ rel_i / log2(i+1) (rank i from 1); NDCG = DCG/IDCG via `search_relevance_engineering_calc.py relevance` (§3 #1).

## Step 3 — Compute MRR + precision@k
MRR for first-relevant; precision@k for top-k quality (§3 #1).

## Step 4 — Baseline before tuning
Record the baseline; every change reports a before/after delta (§3 #1 #3).

## Output
An NDCG/MRR/precision@k read against the judgment list with a baseline. Traverse Tree 1 in the decision-trees file.
