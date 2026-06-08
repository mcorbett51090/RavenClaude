---
scenario_id: 2026-06-08-swapped-model-it-was-retrieval
contributed_at: 2026-06-08
plugin: ai-rag-engineering
product: retrieval
product_version: "n/a"
scope: likely-general
tags: [retrieval, recall, eval, model-swap]
confidence: medium
reviewed: false
---

## Problem

A RAG app gave wrong answers and the team upgraded to a larger, costlier LLM, which didn't help. The risk: an LLM can only ground on what it's retrieved, so a retrieval failure looks like a model failure — and swapping the model wastes cost while leaving the real bug untouched (§3 #1).

## Context

- Corpus: technical docs with codes and IDs; pure-vector retrieval.
- Constraint: retrieval quality caps generation — measure recall@k before touching the model (§3 #1).
- The team reasoned from output quality, skipping retrieval.

## Attempts

- Tried: **measured recall@k on a judgment set** (`ai_rag_engineering_calc.py retrieval-eval`). Outcome: recall@k was low — the answering passage often wasn't in the top-k, so no model could ground on it (§3 #1).
- Tried: **added hybrid search** (BM25 + vector fusion) for the keyword/ID-heavy queries (§3 #6). Outcome: recall@k rose sharply on exactly those queries.
- Tried: **re-ran the eval on the original, cheaper model** with improved retrieval. Outcome: answers improved without the model upgrade — the upgrade had been treating the wrong layer (§3 #1).

## Resolution

The fix was to **repair retrieval (hybrid search) and revert to the cheaper model**, validated by a before/after eval — **not** the model swap. The output was the recall@k read, the hybrid-vs-vector comparison, and the eval delta.

**Action for the next consultant hitting this pattern:** **measure recall@k before swapping the model.** Retrieval quality caps generation; a retrieval bug masquerades as a model bug. Try hybrid search for keyword/ID-heavy corpora before reaching for a bigger LLM. See Tree 2 and the `retrieval-eval` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
