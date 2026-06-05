---
scenario_id: 2026-06-05-declarative-agent-scope-too-broad
contributed_at: 2026-06-05
plugin: microsoft-365-copilot
product: declarative-agent
product_version: "DA manifest v1.7"
scope: likely-general
tags: [declarative-agent, instructions, scope, grounding, rai-validation, hallucination]
confidence: medium
reviewed: false
---

## Problem

A team shipped a declarative agent meant to answer questions about one product line's support policy. In testing it gave confident, plausible-sounding answers that were **wrong** — it answered questions about *other* product lines (which it had no grounding for) and about pricing (out of scope entirely), inventing details. The `instructions` block had grown to ~7,600 of the ~8,000-char budget by accreting "also handle X" clauses, and the grounding was pointed at an entire SharePoint site rather than the support-policy library.

## Context

- Declarative agent (manifest v1.7), authored in Agents Toolkit, grounded on SharePoint knowledge.
- The agent passed RAI validation on sideload and the manifest was schema-valid — so "it built fine" masked that it was *behaviorally* wrong. Schema validity is not behavioral correctness (CLAUDE.md §3 #15).
- No golden-prompt regression set existed; "done" had meant "the manifest validates and it answers the happy-path demo prompt."

## Attempts

- Tried: adding more "do NOT answer about pricing" sentences to the instructions. Marginal — it pushed the block closer to the budget ceiling and the model still drifted, because the *grounding* still reached pricing-adjacent content.
- Tried: narrowing the grounding from the whole site to the specific support-policy document library, and traversing the grounding-source decision tree ([`../knowledge/grounding-source-decision-2026.md`](../knowledge/grounding-source-decision-2026.md)) to confirm SharePoint knowledge (not a connector) was right for already-governed SharePoint content. Outcome: the off-domain hallucinations dropped sharply — most "wrong product line" answers came from over-broad grounding, not the prompt.
- Tried (the moves that worked together): (a) cut the instructions back to **persona + scope + one explicit out-of-scope guardrail sentence**, moving scenario-specific prompt guidance into **conversation starters** (which users invoke) rather than the always-read instruction block — traversing the "does the instruction set need a redesign?" tree in [`../knowledge/copilot-extensibility-decision-trees.md`](../knowledge/copilot-extensibility-decision-trees.md); (b) designed to ~66% of the 8K budget, not the ceiling (CLAUDE.md §3 #3); (c) built a **golden-prompt regression set** including adversarial off-scope prompts ("what does product Y cost?") and asserted the agent redirects rather than answers.

## Resolution

The root cause was **two scope leaks, not one**: over-broad grounding (the bigger lever) *and* an over-stuffed instruction block trying to compensate. The fix was to tighten the grounding to exactly the support-policy library, slim the instructions to persona/scope/guardrail with scenario prompts moved to conversation starters, and gate "done" on a golden-prompt set that includes adversarial off-scope prompts.

**Action for the next engineer hitting this pattern:** when a declarative agent answers confidently-but-wrong, suspect **grounding scope before the prompt** — narrow the knowledge source to exactly the in-scope content, then trim instructions to behavior (persona + scope + one out-of-scope guardrail) and push scenario guidance to conversation starters. Never declare a DA done without a golden-prompt regression set that includes adversarial off-scope prompts (CLAUDE.md §3 #15). The instruction-redesign and grounding-source trees in the knowledge bank are the canonical references; this is a single field note behind them.

**Sources (retrieved 2026-06-05):**
- Declarative agent instructions / character budget — Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-declarative-agent and the manifest schema docs (v1.7) — `[verify-at-build]`, the manifest ships ~monthly.
- RAI validation runs on sideload/publish — Microsoft Learn extensibility docs (validate-and-publish). `[verify-at-build]`.
