---
scenario_id: 2026-06-08-more-context-made-it-worse
contributed_at: 2026-06-08
plugin: ai-rag-engineering
product: serving-cost
product_version: "n/a"
scope: likely-general
tags: [context-economics, token-cost, lost-in-the-middle, precision]
confidence: medium
reviewed: false
---

## Problem

To improve answers, a team increased top-k to send many more chunks per query. Cost and latency rose, and faithfulness on the eval dropped. The risk: more context is not better — it costs tokens, raises latency, and can degrade quality via lost-in-the-middle and distractor passages (§3 #5).

## Context

- Endpoint: customer-facing RAG, latency-sensitive.
- Constraint: retrieve the fewest high-precision chunks that answer the question, not the most that fit (§3 #5).
- The team equated more context with better grounding.

## Attempts

- Tried: **measured cost per request at the higher top-k** (`ai_rag_engineering_calc.py token-cost`). Outcome: input tokens (dominated by context) drove cost and latency up materially (§3 #5).
- Tried: **re-ran the eval** at the higher top-k. Outcome: faithfulness and answer-relevance DROPPED — distractor passages and lost-in-the-middle (§3 #5).
- Tried: **cut to the fewest high-precision chunks** and improved precision@k via better ranking. Outcome: quality recovered and cost fell — the opposite of the intuition (§3 #5).

## Resolution

The fix was to **reduce top-k to high-precision chunks and improve ranking**, not to maximize context — cheaper AND better, validated on the eval. The output was the token-cost read, the eval delta at each top-k, and the recommended context size.

**Action for the next consultant hitting this pattern:** **retrieve the fewest high-precision chunks, not the most that fit.** More context costs tokens and can degrade quality. Validate top-k changes on the eval and watch faithfulness, not just cost. See Tree 3 and the `token-cost` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
