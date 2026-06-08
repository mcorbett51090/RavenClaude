---
description: "Read RevPAR as ADR × occupancy and test the rate-vs-occupancy trade-off; carry to GOPPAR if profit is given. Reach for this on a rate or RevPAR question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read RevPAR

You are running `/hotel-hospitality-operations:read-revpar` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the room base — Rooms available and rooms sold for the period.
2. Compute RevPAR — Occupancy, ADR, and RevPAR via `hotel_hospitality_operations_calc.py revpar` (§3 #1).
3. Test the trade-off — Does a rate change lift or erode the product against the demand curve (§3 #1).
4. Carry to GOPPAR — If total revenue + GOP given, compute GOPPAR — profit beats top line (§3 #5).

## Output
A RevPAR (and optional GOPPAR) read with the rate-vs-occupancy trade-off named. Traverse Tree 1 in the decision-trees file. See [`../skills/read-revpar/SKILL.md`](../skills/read-revpar/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No guest PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
