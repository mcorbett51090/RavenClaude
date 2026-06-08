---
description: "Compare channels at net rate after acquisition cost, not gross rate. Reach for this on a channel or OTA question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Compare channels

You are running `/hotel-hospitality-operations:compare-channels` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the gross rate — The room rate the guest pays on each channel.
2. Subtract acquisition cost — OTA commission vs direct acquisition cost via `hotel_hospitality_operations_calc.py channel-cost` (§3 #2).
3. Compare net rate — The margin each channel actually keeps.
4. Value direct demand — Repeat/direct lowers long-run acquisition cost (§3 #2 #6).

## Output
A net-rate comparison naming the better channel for the margin. See [`../skills/compare-channels/SKILL.md`](../skills/compare-channels/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No guest PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
