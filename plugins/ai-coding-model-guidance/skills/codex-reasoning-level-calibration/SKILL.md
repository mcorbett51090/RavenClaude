---
name: codex-reasoning-level-calibration
description: "Calibrate the OpenAI Codex reasoning-level dial before recommending a model upgrade. Maps task type, failure mode, and budget to the right reasoning effort level — ensuring developers exhaust the reasoning dial on the current model before paying for a bigger SKU. Domain-specific to the Codex reasoning API."
---

# Skill: Codex Reasoning-Level Calibration

The Codex reasoning-level dial is a cost-effective lever that most developers skip. Before upgrading to a bigger Codex SKU, try raising reasoning effort on the current model. This skill ensures the reasoning dial is calibrated correctly before a model upgrade is recommended.

## When to reach for this skill

- Output quality is insufficient on the Codex default model at default reasoning.
- The developer is considering upgrading to a frontier Codex model.
- The task is latency-tolerant (background runs, supervised agentic work, large refactors).

**Do not apply** to inline completions or interactive chat where latency is the binding constraint — raising reasoning effort increases latency in a way users feel immediately.

## Step 1 — Classify the failure mode

Different failure modes call for different reasoning levels:

| Failure mode | Signal | Reasoning-dial response |
|---|---|---|
| Shallow logic errors | Plausible-but-wrong code; misses obvious constraints | Raise reasoning to medium-high |
| Missing context integration | Ignores established patterns in the codebase | Raise reasoning + improve prompt context |
| Incomplete multi-step plans | Stops early on multi-file or multi-step tasks | Raise reasoning to high; or decompose the task |
| Wrong tool/API choice | Picks a deprecated or incorrect API | Raise reasoning + provide explicit API list |
| Nondeterministic quality | Excellent sometimes, poor other times | Raising reasoning reduces variance; test at high |

## Step 2 — Map to reasoning level

OpenAI Codex exposes reasoning effort as a dial (exact parameter name and values: verify-at-use against the current API — (verify-at-use — 2026-06)):

| Level | Cost delta | Latency delta | Use when |
|---|---|---|---|
| Low / off | 1x baseline | Lowest | Autocomplete, quick edits |
| Medium | Moderate increase | Moderate | Most supervised coding tasks |
| High | Larger increase | Higher | Hard multi-file tasks, long agentic runs |
| Max | Highest | Highest | Hardest tail; before considering a model upgrade |

**Rule:** exhaust the reasoning-level dial on the current model before upgrading the model. A model upgrade multiplies the per-token cost; raising reasoning effort increases cost more modestly.

## Step 3 — Test the calibration

Run the failing task at the next reasoning level up. Accept the result if:

1. The failure mode from Step 1 is resolved.
2. Latency is still acceptable for the task's interactivity requirement.
3. The cost delta is within the task's budget.

If all three hold, the new reasoning level is the recommendation — not a model upgrade.

## Step 4 — When reasoning dial is at max and still failing

Document:
- Task description and why it's failing at max reasoning.
- That reasoning has been exhausted on the current model.
- Whether task decomposition (splitting into smaller steps) could substitute for a model upgrade.

Only after confirming that decomposition won't close the gap does this skill hand off to `codex-model-strategist` with a recommendation to upgrade the model SKU.

## Pitfalls

- Jumping straight to a model upgrade because "the default isn't working" — the reasoning dial is almost always cheaper.
- Applying high reasoning to interactive chat — the latency impact is felt immediately by users.
- Treating "reasoning level" as a binary (on/off) — it is a spectrum; test incrementally.
- Forgetting to document that the dial was exhausted before recommending an upgrade — the next engineer will otherwise repeat the calibration.

## See also

- [`../../agents/codex-model-strategist.md`](../../agents/codex-model-strategist.md) — the agent that owns Codex model selection
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — the Codex reasoning/upgrade decision tree
- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — the dated Codex lineup with reasoning-level notes
