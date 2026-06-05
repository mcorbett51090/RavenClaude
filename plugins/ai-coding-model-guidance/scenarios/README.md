# AI-coding model-guidance scenarios bank

> Unverified, dated, scope-tagged narratives from real (or realistic) model-selection engagements across the **non-Claude** AI-coding ecosystems (GitHub Copilot · OpenAI Codex · xAI Grok). Enabled as part of the value-add build-out (2026-06-05).

This directory holds **scenarios** — war stories of "a developer reached for model X, here was the task, these were the constraints, A/B/C were tried, D was the right-sized call." Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble (see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md))

Unlike a practice-operations scenarios bank, these are **model-selection engagements**: a Copilot picker call for a big refactor, a Codex reasoning-level decision on a hard bug, a Grok cost-vs-capability trade, a right-sizing call that avoided silent spend, or a closed-world "that model doesn't exist" catch. The "Resolution" is a **right-sized tier choice plus the reasoning that got there** — not a code fix.

## The schema (mirrors the marketplace 9-field scenario schema)

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: ai-coding-model-guidance
product: <copilot | codex | grok | cross-tool>
product_version: "n/a"          # advisory knowledge vertical — no product version
scope: tool-specific | segment-specific | likely-general
tags: [list of 3-7 keywords]
confidence: low | medium | high
reviewed: false
---

## Problem
## Context              (ecosystem, surface/plan, constraints — the analogue of "Permissions context")
## Attempts
## Resolution
```

> **Volatility discipline:** every model name, price, context window, reasoning level, or retirement referenced in a scenario carries a **retrieval date** and/or a `[verify-at-use]` marker, exactly as the [`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md) lineup does. A scenario is a **narrative about the reasoning**, not a fresh source of truth for a SKU or a number — re-verify any specific against the dated lineup before quoting. The **closed-world rule** applies in scenarios too: never name a model absent from the verified lineup.

## What's in this bank

| File | Scope | Tags | Confidence |
|---|---|---|---|
| [`2026-06-05-copilot-picker-refactor-vs-completion.md`](2026-06-05-copilot-picker-refactor-vs-completion.md) | likely-general | github-copilot, picker, big-refactor, inline-completion, right-sizing, auto | medium |
| [`2026-06-05-codex-reasoning-level-before-model-upgrade.md`](2026-06-05-codex-reasoning-level-before-model-upgrade.md) | likely-general | openai-codex, reasoning-level, hard-bug, model-upgrade, cost-per-resolved-task | medium |
| [`2026-06-05-grok-code-fast-1-retirement-silent-rebill.md`](2026-06-05-grok-code-fast-1-retirement-silent-rebill.md) | likely-general | xai-grok, grok-code-fast-1, retirement, silent-rebill, model-id, migration | high |
| [`2026-06-05-hallucinated-model-closed-world-catch.md`](2026-06-05-hallucinated-model-closed-world-catch.md) | likely-general | closed-world, hallucinated-model, version-pattern, anti-hallucination, lineup | high |

## Promotion path

When ≥2 independent scenarios (different engagements / quarters) corroborate the same finding, an agent may propose promoting the lesson into [`../best-practices/`](../best-practices/) or a [`../knowledge/`](../knowledge/) decision tree. As of this bank's creation, promotion is manual — leave the scenario in place even after the rule is canonicalized (the narrative stays useful as context).

## How agents use this bank

Per [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md): surface a matching scenario only as a *secondary* source, always behind the unverified-scenario preamble, and never let a scenario override the cited knowledge bank or the closed-world rule. The most-likely-to-benefit specialists — `copilot-model-strategist`, `codex-model-strategist`, `grok-model-strategist` — should check the bank when a situation matches.
