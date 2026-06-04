---
description: "Read inventory turns as both a cash and a compliance metric, flagging aged and perishable product. Reach for this on a cash or expiry question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read inventory turns

You are running `/cannabis-operations:read-inventory-turns` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute turns by category — Turns and days-on-hand by category (§3 #5).
2. Flag the perishable — Surface aged flower nearing expiry.
3. Tie to cash — Quantify the cash trapped in slow inventory.
4. Act — Reorder, discount-to-clear, or remediate before write-off.

## Output
A turns-by-category read, perishable flags, the trapped cash, and a clearance action. See [`../skills/read-inventory-turns/SKILL.md`](../skills/read-inventory-turns/SKILL.md). Traverse the matching tree in [`../knowledge/cannabis-decision-trees.md`](../knowledge/cannabis-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
