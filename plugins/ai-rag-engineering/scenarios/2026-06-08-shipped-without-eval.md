---
scenario_id: 2026-06-08-shipped-without-eval
contributed_at: 2026-06-08
plugin: ai-rag-engineering
product: eval
product_version: "n/a"
scope: likely-general
tags: [eval, faithfulness, judgment-set, regression]
confidence: medium
reviewed: false
---

## Problem

A team changed chunk size to reduce cost and shipped without an offline eval, trusting spot-checks. Hallucinations rose in production. The risk: a RAG change without a before/after eval is shipping on vibes — chunking is a retrieval decision, and a silent recall regression surfaces as hallucination downstream (§3 #2 #3).

## Context

- Stack: production RAG, no judgment set.
- Constraint: eval before you ship — build a judgment set and measure before/after (§3 #3).
- The team relied on a few manual spot-checks.

## Attempts

- Tried: **built a judgment set retroactively** (queries + relevant passages + ideal answers) (§3 #3). Outcome: a reusable offline harness the team should have had first.
- Tried: **measured recall@k and faithfulness at the old vs new chunk size** (`ai_rag_engineering_calc.py retrieval-eval`). Outcome: the smaller chunks had split answering units, dropping recall@k — a chunking bug surfacing as hallucination (§3 #2).
- Tried: **gated future changes on the eval delta**, with structure-aware chunking to keep units intact (§3 #2 #3).

## Resolution

The fix was to **build the eval, revert to a structure-aware chunking that held recall, and gate every change on a before/after eval** — **not** to keep relying on spot-checks. The output was the eval harness, the recall regression diagnosis, and the eval-gate process.

**Action for the next consultant hitting this pattern:** **no eval, no ship — and chunking changes are retrieval changes.** Build a judgment set, baseline it, and require a before/after delta on every change. A silent recall regression surfaces as hallucination. See Tree 1 and the `retrieval-eval` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
