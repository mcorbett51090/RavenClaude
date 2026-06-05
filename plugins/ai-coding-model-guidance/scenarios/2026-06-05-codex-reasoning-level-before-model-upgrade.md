---
scenario_id: 2026-06-05-codex-reasoning-level-before-model-upgrade
contributed_at: 2026-06-05
plugin: ai-coding-model-guidance
product: codex
product_version: "n/a"
scope: likely-general
tags: [openai-codex, reasoning-level, hard-bug, model-upgrade, cost-per-resolved-task]
confidence: medium
---

## Problem

A developer using OpenAI Codex (CLI) was stuck on a hard, intermittent concurrency bug — a race that only surfaced under load and that the default model kept "fixing" with plausible-but-wrong patches. Their instinct was to **upgrade to the biggest/most-expensive Codex model in the lineup** ("throw the frontier model at it"). They asked the strategist to confirm the upgrade and were ready to eat the larger per-token bill for the whole session.

## Context

- Ecosystem: OpenAI Codex, CLI surface, supervised (developer watching each diff — not an unsupervised agent run).
- The task was **reasoning-bound, not latency-bound**: the developer was fine waiting longer for a correct answer; what they could not tolerate was another confidently-wrong patch.
- Codex exposes an explicit **reasoning-effort dial** (levels reported as minimal / low / medium / high / xhigh — `[verify-at-use — 2026-06-05]` against the live `--help` / config, since level names and defaults churn). A crucial Codex-specific nuance verified this date: **cost is determined by the model selected, not by the reasoning level — the only downside of a higher reasoning level is increased latency** ([OpenAI Codex models](https://developers.openai.com/codex/models), retrieved 2026-06-05 `[verify-at-use]`).
- The developer was running the **default model at its default (medium-ish) reasoning level** and had not yet tried raising the dial.

## Attempts

- Tried: framed the fix as "upgrade to the frontier Codex model." Outcome: premature — it skips the cheaper lever (the reasoning dial) and, given the cost-is-by-model nuance, pays a model-tier premium for what might be a thinking-budget problem. Abandoned as the first move.
- Tried: traversed the **Codex reasoning-dial tree** in [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) ("Codex — default model, reasoning dial, or model upgrade?"). Task is not latency-sensitive → default already tried → **dial available and not at max** → raise reasoning level on the *same* model before upgrading. Outcome: identified the right next step.
- Tried (the move that worked): raised the reasoning level to **high** on the same default model and re-ran with a sharpened prompt that named the race condition explicitly. Outcome: the model produced a correct, lock-ordering fix that held under the load repro. Because cost is set by the model and not the reasoning level, the only thing the developer "paid" for the higher level was a longer wait — not a bigger bill.

## Resolution

The lever was **reasoning effort, not model tier**. On Codex specifically, raising the reasoning dial on the same model trades latency for depth at (verified this date) no change in per-token model cost — so the dial should be exhausted before a model upgrade for any reasoning-bound, latency-tolerant task. The model upgrade is still the right move for the genuine hard tail (a task that fails even at the top reasoning level on the balanced model, or a long unsupervised agentic run) — but it was not the right *first* move here.

**Action for the next strategist hitting this pattern:** when a Codex user says "the default isn't getting it, I'll upgrade the model," first ask whether the task is latency-tolerant (it usually is, for a hard bug). If so, **raise the reasoning level on the current model and re-prompt before upgrading** — and explain the Codex-specific economics: higher reasoning level costs latency, not dollars; the model choice is what moves the bill. Re-verify the live reasoning-level names/defaults and that cost-by-model nuance against [the Codex models doc](https://developers.openai.com/codex/models) `[verify-at-use]` before quoting — both can change. Cross-reference [`../best-practices/reasoning-level-before-model-upgrade.md`](../best-practices/reasoning-level-before-model-upgrade.md) and [`../best-practices/right-size-not-top-of-range.md`](../best-practices/right-size-not-top-of-range.md).

**Sources / verify-at-use:** reasoning-level names, the default model id, and the cost-is-by-model behavior are volatile — re-verify against [OpenAI Codex models](https://developers.openai.com/codex/models) and [OpenAI model release notes](https://help.openai.com/en/articles/9624314-model-release-notes) before quoting (snapshot `[verify-at-use — 2026-06-05]`). No specific per-token price is quoted here by design — it is the fastest-churning number and lives, dated, in [`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md).
