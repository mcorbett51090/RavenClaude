---
scenario_id: 2026-06-05-grok-code-fast-1-retirement-silent-rebill
contributed_at: 2026-06-05
plugin: ai-coding-model-guidance
product: grok
product_version: "n/a"
scope: likely-general
tags: [xai-grok, grok-code-fast-1, retirement, silent-rebill, model-id, migration]
confidence: high
---

## Problem

A team had wired the xAI Grok API into a custom CI step that ran a coding agent on every PR, pinned to the model id **`grok-code-fast-1`** — chosen months earlier specifically because it was the cheap, fast, agentic-coding SKU. Nothing in their pipeline broke: requests kept succeeding, the agent kept running. But their monthly xAI bill had climbed noticeably with no change in PR volume, and nobody could explain why. They asked "did Grok raise prices on grok-code-fast-1?"

## Context

- Ecosystem: xAI Grok, **API surface** (not an IDE picker), inside an automated CI pipeline — so there was no human watching a model dropdown to notice a change.
- The model id `grok-code-fast-1` is **retired** (retirement date **2026-05-15** per the dated lineup; `[verify-at-use]`). The critical, easy-to-miss mechanic: **the old slug still resolves** — requests do not error — but they **redirect to Grok 4.3 and are billed at Grok 4.3 pricing** ([`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md) Grok section, retrieval 2026-05-31 `[verify-at-use]`; corroborated by [xAI migration notice](https://docs.x.ai/developers/migration/may-15-retirement)). So the pipeline "works" while silently billing at a different, higher rate than the historical cheap grok-code-fast-1 rate.
- Because the failure is a **silent rebill**, not an error, it does not show up in logs or alerts — only on the invoice.

## Attempts

- Tried: investigated as "did the price of grok-code-fast-1 change?" Outcome: wrong frame — the model no longer exists; you cannot reason about "its price." Abandoned.
- Tried: checked the **retirement / closed-world** section of the lineup and the [xAI model migration notice](https://docs.x.ai/developers/migration/may-15-retirement). Outcome: confirmed the slug is retired and redirects, which is exactly the silent-rebill signature.
- Tried (the move that worked): treated this as the canonical **retirement-with-billing-consequence** case (house opinion #7). Told the team to (a) stop pinning the retired slug, (b) explicitly re-pin a **current, verified** model id from the dated lineup sized to the task — a fast/cheap tier for the high-volume per-PR loop, not the flagship — and (c) re-verify the chosen id and its pricing against the live xAI models page before committing, because the migration target itself is volatile (one source recommended a build-tier coding SKU as the migration path rather than the flagship — `[verify-at-use]`). Outcome: spend came back under control and, more importantly, became *legible* — the pinned id now matches what they are actually billed for.

## Resolution

The bill climbed because a **retired model id silently redirected to a higher-priced model** while the code kept working. The fix is not "find grok-code-fast-1's new price" (it has none) — it is to migrate off the retired slug to a current, verified, right-sized id and re-verify its pricing at use. This is the single highest-value correction this plugin makes, precisely because it produces no error to trip over.

**Action for the next strategist hitting this pattern:** whenever a consumer is still naming **`grok-code-fast-1`** (or any retired slug), lead with the retirement + silent-rebill warning *before* anything else — do not let them keep eating the redirect. Then right-size the replacement (the per-PR loop wants a fast/cheap tier, not the flagship) and re-verify the current id + price against [the xAI models doc](https://docs.x.ai/developers/models) and [the migration notice](https://docs.x.ai/developers/migration/may-15-retirement) `[verify-at-use]`. Cross-reference [`../best-practices/flag-retirements-first.md`](../best-practices/flag-retirements-first.md) and [`../best-practices/right-size-not-top-of-range.md`](../best-practices/right-size-not-top-of-range.md).

**Sources / verify-at-use:** the retirement date, the redirect target, and all Grok pricing are volatile — re-verify against [xAI models](https://docs.x.ai/developers/models) and the [May 15 retirement notice](https://docs.x.ai/developers/migration/may-15-retirement) before quoting (lineup snapshot `[verify-at-use — 2026-05-31]`; retirement date `2026-05-15`). No specific per-token price is restated in this scenario by design — it lives, dated, in the lineup.
