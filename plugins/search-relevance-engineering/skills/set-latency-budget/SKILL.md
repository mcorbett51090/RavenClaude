---
name: set-latency-budget
description: "Set a p95 latency budget, decompose per-stage latency, and tune relevance within it. Reach for this on a speed/capacity question."
---

# Skill: Set latency budget

Don't chase NDCG into a timeout (§3 #4).

## Step 1 — Set the p95 budget
A target the search must hold via `search_relevance_engineering_calc.py latency-budget` (§3 #4).

## Step 2 — Decompose per stage
Query, fetch, rescore — find the slow stage (§3 #4).

## Step 3 — Size the index
Shards/replicas/storage via `search_relevance_engineering_calc.py index-sizing` (§3 #7).

## Step 4 — Tune relevance within budget
Buy relevance with rescoring only inside the headroom (§3 #4 #5).

## Output
A p95 latency budget with per-stage decomposition and the relevance headroom. Traverse Tree 3 in the decision-trees file.
