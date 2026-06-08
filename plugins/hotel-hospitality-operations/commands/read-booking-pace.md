---
description: "Read booking pace and pickup against the prior cycle to decide hold-rate vs stimulate. Reach for this on a forecast or pace question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read booking pace

You are running `/hotel-hospitality-operations:read-booking-pace` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set on-the-books — Rooms on the books for the target period.
2. Compare to pace — Vs the same point last cycle/last year — pickup and pace (§3 #3).
3. Read length-of-stay and segment — How committed (group/corporate) the pace is (§3 #7).
4. Decide hold vs stimulate — Hold rate when ahead; stimulate demand when behind (§3 #3).

## Output
A pace/pickup read telling whether to hold rate or stimulate demand. See [`../skills/read-booking-pace/SKILL.md`](../skills/read-booking-pace/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No guest PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
