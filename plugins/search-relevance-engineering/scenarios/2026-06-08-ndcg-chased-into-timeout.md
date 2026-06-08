---
scenario_id: 2026-06-08-ndcg-chased-into-timeout
contributed_at: 2026-06-08
plugin: search-relevance-engineering
product: query-performance
product_version: "n/a"
scope: likely-general
tags: [latency-budget, rescore, tradeoff, p95]
confidence: medium
reviewed: false
---

## Problem

To squeeze out more relevance, a team grew the candidate set and added deep rescoring; NDCG rose but p95 latency breached the interactive budget. The risk: latency vs relevance is a real tradeoff, and chasing NDCG into a timeout trades a metric users feel (speed) for one they may not (a marginal ranking gain) (§3 #4).

## Context

- Search: interactive, latency-sensitive UX.
- Constraint: set a p95 latency budget and tune relevance within it (§3 #4).
- The team optimized NDCG without a latency budget.

## Attempts

- Tried: **set a p95 latency budget and decomposed per-stage latency** (`search_relevance_engineering_calc.py latency-budget`). Outcome: rescore depth dominated the time and pushed p95 over budget (§3 #4).
- Tried: **measured the marginal NDCG per unit of rescore depth.** Outcome: most of the relevance gain came from a fraction of the rescore depth — diminishing returns (§3 #4).
- Tried: **trimmed the candidate set and rescore depth to fit the budget**, holding most of the NDCG gain. Outcome: relevance within the latency budget, not beyond it.

## Resolution

The fix was to **tune relevance within an explicit p95 budget**, trading marginal rescore depth for speed — **not** to chase NDCG past the budget. The output was the latency budget, the per-stage decomposition, and the relevance-within-budget setting.

**Action for the next consultant hitting this pattern:** **set a p95 latency budget and tune relevance inside it.** Relevance levers cost latency, and the marginal NDCG gain often isn't worth the marginal latency. Decompose per-stage and trade depth for speed explicitly. See Tree 3 and the `latency-budget` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
