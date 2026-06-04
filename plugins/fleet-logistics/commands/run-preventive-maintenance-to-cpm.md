---
description: "Run a PM program against maintenance CPM and downtime so a deferred PM doesn't become a roadside failure. Reach for this when repair costs rise."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Run preventive maintenance to CPM

You are running `/fleet-logistics:run-preventive-maintenance-to-cpm` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Read maintenance CPM — Maintenance cost ÷ miles, by truck and age (§3 #5).
2. Measure unplanned downtime — Separate planned PM from unplanned failures.
3. Tighten the PM schedule — Set PM intervals that beat the failure curve.
4. Call replacement on lifecycle — Replace when rising maintenance CPM exceeds new-iron cost.

## Output
A maintenance-CPM read, a downtime split, a PM schedule, and a lifecycle replacement call. See [`../skills/run-preventive-maintenance/SKILL.md`](../skills/run-preventive-maintenance/SKILL.md). Traverse the matching tree in [`../knowledge/fleet-decision-trees.md`](../knowledge/fleet-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
