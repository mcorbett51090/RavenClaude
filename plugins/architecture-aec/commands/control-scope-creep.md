---
description: "Distinguish in-scope iteration from additional services and authorize the difference, so unbilled changes don't erode the fee. Reach for this when the design keeps changing."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Control scope creep

You are running `/architecture-aec:control-scope-creep` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Define the baseline scope — What the fee covers, by phase (§3 #2).
2. Flag the creep — Identify out-of-scope options and changes.
3. Authorize additional services — Route the change to an additional-services authorization.
4. Protect the gate — Don't advance phases without approval (§3 #6).

## Output
A scope baseline, flagged creep, an additional-services path, and a protected gate. See [`../skills/control-scope-creep/SKILL.md`](../skills/control-scope-creep/SKILL.md). Traverse the matching tree in [`../knowledge/aec-decision-trees.md`](../knowledge/aec-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
