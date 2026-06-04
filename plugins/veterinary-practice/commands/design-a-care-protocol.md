---
description: "Build an evidence-aligned, standardized care protocol as decision-support for the licensed DVM, to reduce unwarranted variation. Reach for this on a common presentation worked up inconsistently."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Design a care protocol

You are running `/veterinary-practice:design-a-care-protocol` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Scope the presentation — Define the presentation and the decision points (history, diagnostics, treatment).
2. Align to evidence and stay decision-support — Build the protocol to current guidance, framed as support for the DVM, never an order (§3 #1).
3. Standardize the estimate — Tie the protocol to a consistent estimate so recommended-care presentation is uniform (§3 #4).
4. Plan adoption — Define how DVMs adopt and where deviation is expected and documented.

## Output
A protocol pack with decision points, a standard estimate, and an adoption plan — as DVM decision-support. See [`../skills/design-care-protocol/SKILL.md`](../skills/design-care-protocol/SKILL.md). Traverse the matching tree in [`../knowledge/vet-decision-trees.md`](../knowledge/vet-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
