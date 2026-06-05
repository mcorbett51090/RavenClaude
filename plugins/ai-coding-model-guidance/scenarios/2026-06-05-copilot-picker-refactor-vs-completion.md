---
scenario_id: 2026-06-05-copilot-picker-refactor-vs-completion
contributed_at: 2026-06-05
plugin: ai-coding-model-guidance
product: copilot
product_version: "n/a"
scope: likely-general
tags: [github-copilot, picker, big-refactor, inline-completion, right-sizing, auto]
confidence: medium
---

## Problem

A developer on GitHub Copilot Pro had pinned the top frontier model in the picker "so the suggestions are always the best," and used it for *everything* — including inline autocomplete while typing. They reported two complaints that are the classic mis-fit signature: (a) inline completions felt **laggy** (a beat of latency on every keystroke-triggered suggestion), and (b) their monthly premium-request budget was burning down far faster than a teammate doing comparable work. They wanted to know whether to "upgrade the plan" or "switch to a different tool."

## Context

- Ecosystem: GitHub Copilot, Pro plan, VS Code. Surfaces in play: **inline completions** (the laggy one) and the **chat/edit** surface (where the refactor work happened).
- Constraint: latency on inline completion is a UX constraint — a completion that arrives after you've typed past it is worse than no completion. The frontier model's reasoning depth is wasted on a single-line completion and costs latency.
- The genuinely hard work — a cross-cutting refactor of an auth module spanning ~12 files — was real frontier-tier work, but it was a *fraction* of the day; most of the day was inline completion + small edits.
- The picker offers an **`Auto`** option that right-sizes per request (verify the current `Auto` behavior + the per-surface model list against the live picker — `[verify-at-use — 2026-05-31 snapshot]`).

## Attempts

- Tried: framed the complaint as a single "which model is best" question. Outcome: wrong frame — it collapses two different tasks (latency-bound completion vs hard refactor) onto one SKU. Abandoned.
- Tried: traversed the vendor-neutral tier tree in [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) per task. Inline completion → **fast/cheap tier** (latency is the binding constraint, quality gap on a one-liner is small). The 12-file auth refactor → autonomous/hard branch → **frontier tier** is justified *for that task only*. Outcome: identified that one pin can't serve both.
- Tried (the move that worked): set the picker to **`Auto`** for the default day-to-day flow so completions get a fast tier and chat/edit escalates when the task warrants, and **manually pin the frontier model only for the duration of the refactor session**, then drop back. Outcome: inline lag disappeared (fast tier serves completions) and the premium-request burn dropped to roughly the teammate's level, because the frontier model was now paid for only on the hard tail.

## Resolution

The problem was **one model pinned across two task shapes with opposite constraints**, not a wrong plan or a wrong tool. Right-sizing per task — fast tier for latency-bound completion, frontier reserved for the genuinely-hard refactor — fixed both the lag and the spend. The metric that decides this is **cost-per-resolved-task**, not "which model is ranked highest" (a frontier model that resolves a one-line completion and a fast model that resolves it have the *same* outcome and very different bills + latency).

**Action for the next strategist hitting this pattern:** when someone says "I pinned the best model and it's slow/expensive," do **not** answer "which model is best." Split their day by task shape first (inline completion vs interactive edit vs autonomous multi-file run), traverse the tier tree per shape, and default to **`Auto`** unless the tree gives a specific reason to override — then pin the top tier only for the bounded hard-task session. Cross-reference the right-sizing rule in [`../best-practices/right-size-not-top-of-range.md`](../best-practices/right-size-not-top-of-range.md) and the surface-scoping rule in [`../best-practices/scope-availability-surface-plan-date.md`](../best-practices/scope-availability-surface-plan-date.md).

**Sources / verify-at-use:** the exact `Auto` behavior, the per-surface model lists, and plan-gated availability churn weekly-to-monthly — re-verify against the live picker in `github.com/copilot` and the [GitHub Copilot supported-models doc](https://docs.github.com/en/copilot/reference/ai-models/supported-models) before quoting any specific model name to a client (the lineup snapshot here is `[verify-at-use — 2026-05-31]`). No specific premium-request price is quoted in this scenario precisely because it is the fastest-churning number.
