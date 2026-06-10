---
description: "Set a p95 latency budget, decompose per-stage latency, and tune relevance within it. Reach for this on a speed/capacity question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Set latency budget

You are running `/search-relevance-engineering:set-latency-budget` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the p95 budget — A target the search must hold via `search_relevance_engineering_calc.py latency-budget` (§3 #4).
2. Decompose per stage — Query, fetch, rescore — find the slow stage (§3 #4).
3. Size the index — Shards/replicas/storage via `search_relevance_engineering_calc.py index-sizing` (§3 #7).
4. Tune relevance within budget — Buy relevance with rescoring only inside the headroom (§3 #4 #5).

## Output
A p95 latency budget with per-stage decomposition and the relevance headroom. Traverse Tree 3 in the decision-trees file. See [`../skills/set-latency-budget/SKILL.md`](../skills/set-latency-budget/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No query/user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
