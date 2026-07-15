---
name: prompt-pattern-selection
description: "Choose the prompting pattern — zero-shot, few-shot, chain-of-thought, decomposition/chaining, role framing, or self-consistency — by tracing the task against reliability need and token/latency cost. Reach for this when a prompt is inconsistent, when you're about to add examples 'just in case', or when one prompt is quietly doing several jobs. Pairs with structured-output-design."
---

# Skill: Prompting-pattern selection

Pick the **cheapest pattern that clears the reliability bar.** Every step up the
ladder buys reliability with tokens and/or latency — so start low and climb only
on evidence of failure.

## Step 0 — One opinion up front
**Default to zero-shot.** A clear, well-ordered instruction solves more than people
expect. Reach for examples, CoT, or chaining only when a zero-shot prompt *measurably*
fails the hard cases — not preemptively.

## Step 1 — Characterize the failure
Run the prompt on the hard/edge cases and name *how* it fails:
- **Format/style drift** the model can't infer from words → few-shot.
- **Wrong multi-step reasoning** → CoT (one chain) or decomposition (separate jobs).
- **Wrong persona/domain register** → role framing.
- **Occasional wrong high-stakes answer** → self-consistency (sample N, vote).
- **Doing several jobs at once** → decomposition, always.

## Step 2 — Trace the tree
Traverse [`../../knowledge/prompt-decision-trees.md`](../../knowledge/prompt-decision-trees.md) §1
to a leaf. Record the path and the runner-up.

## Step 3 — Price the choice
Name what the pattern costs: few-shot adds input tokens; CoT adds output tokens +
latency; decomposition adds calls (latency, orchestration); self-consistency
multiplies cost by N. If the cost isn't justified by the reliability gain, drop back.

## Step 4 — Verify empirically
Run the chosen pattern against the regression set (owned by
`prompt-reliability-engineer`). Keep it only if it beats the simpler pattern on
*evidence*, not on a single lucky example.

## Step 5 — Hand off
- The **wording + example curation** → `prompt-implementation-engineer`.
- The **eval + regression gate** → `prompt-reliability-engineer`.
- If wording can't fix it, the problem is **architectural** → `prompt-architect`.

## Output
A pattern recommendation with the tree path, the runner-up and why it lost, the
token/latency cost named, and the empirical check that justified it.
