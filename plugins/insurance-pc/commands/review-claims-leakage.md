---
description: "Read indemnity leakage, LAE, and cycle time as managed metrics, not minimized payout, to find the controllable gap. Reach for this on a claims-cost question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Review claims leakage

You are running `/insurance-pc:review-claims-leakage` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure leakage — Indemnity leakage across reserving, settlement, and recovery (§3 #7).
2. Read LAE and cycle time — Loss-adjustment expense and resolution speed.
3. Find the controllable gap — Separate controllable leakage from the loss itself.
4. Tie to reserves — Flag reserve adequacy as the truth behind the result (§3 #5).

## Output
A leakage read, LAE/cycle-time context, the controllable gap, and a reserve-adequacy flag. See [`../skills/review-claims-leakage/SKILL.md`](../skills/review-claims-leakage/SKILL.md). Traverse the matching tree in [`../knowledge/pc-decision-trees.md`](../knowledge/pc-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
