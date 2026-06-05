# Claude app-engineering scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) Claude-app build engagements. Enabled as part of the value-add build-out (2026-06-05) — this retires the `## 8a. Scenarios bank — TODO (planned)` placeholder in [`../CLAUDE.md`](../CLAUDE.md).

This directory holds **scenarios** — field notes of "we hit X building on the Claude API / Agent SDK / MCP, here was the situation, these were the constraints, we tried A/B/C, D worked." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

These are **Claude-app build engagements**: a cache-hit-rate collapse, a tool-use loop that wouldn't terminate, a RAG retrieval miss, a streaming timeout, an eval regression that shipped silently. The "Resolution" is a design/diagnostic move plus the signal that confirmed it — never a guaranteed fix. The canonical reference is always the dated knowledge bank ([`../knowledge/`](../knowledge/)) + `docs/best-practices/`; scenarios never replace it.

## The 9-field schema (the marketplace scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: claude-app-engineering
product: <claude-api | agent-sdk | mcp | prompt-caching | tool-use | rag | evals | finops | streaming>
product_version: "unknown"        # the platform ships monthly — version is rarely pinnable
scope: tenant-specific | likely-general
tags: [3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Constraints context
## Attempts
## Resolution
```

> **Privacy + accuracy:** scenarios carry **no** API keys, no `sk-ant-…` literals, no client-identifying app names, no real cost figures attributable to a named org (illustrative ranges only). Any **dated/volatile platform fact** (model id, price, GA/beta status, context-window size) carries a `[verify-at-use]` marker and defers to [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the platform ships monthly, so a scenario's numbers are a snapshot, not a quote.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-prompt-cache-hit-rate-collapse.md`](2026-06-05-prompt-cache-hit-rate-collapse.md) | likely-general | prompt-caching, cache-hit-rate, cost-blowout, prefix-invalidation, tool-defs | high |
| [`2026-06-05-tool-use-runaway-loop.md`](2026-06-05-tool-use-runaway-loop.md) | likely-general | tool-use, agentic-loop, runaway, max-iterations, idempotency, stop-reason | high |
| [`2026-06-05-rag-retrieval-miss-under-200k.md`](2026-06-05-rag-retrieval-miss-under-200k.md) | likely-general | rag, retrieval, long-context, chunking, reranking, eval-the-retriever | medium |
| [`2026-06-05-streaming-timeout-on-long-output.md`](2026-06-05-streaming-timeout-on-long-output.md) | likely-general | streaming, timeout, max-tokens, backoff, reliability, sse | high |
| [`2026-06-05-eval-regression-shipped-silently.md`](2026-06-05-eval-regression-shipped-silently.md) | likely-general | evals, regression, golden-set, llm-judge, model-migration, ci-gate | medium |

## Promotion path

When ≥2 independent scenarios (different `contributed_at` quarters / engagements) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. Promotion is manual; leave the scenario in place after canonicalization — the narrative stays useful as context.

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble ("Based on N unverified scenarios from YYYY-MM tagged [scope] — verify in your environment before applying"), and never let a scenario override the cited knowledge bank. The most-likely-to-benefit specialists — `prompt-and-context-engineer`, `claude-app-ops-engineer`, `eval-engineer`, `mcp-and-server-tools-engineer` — should check the bank when a situation matches.
