---
description: "Track flash and RAM (image, static, worst-case stack/heap) against the part's limits. Reach for this on any memory or footprint question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Budget memory

You are running `/embedded-iot-engineering:budget-memory` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure the regions — Image size (flash), static RAM, worst-case stack and heap.
2. Compare to the part — Flash and RAM used vs available per region via `embedded_iot_calc.py memory-budget` (§3 #3).
3. Require headroom — Leave margin for stack peaks and OTA dual-bank; no-headroom is over-budget (§3 #3 #5).
4. Flag fragmentation risk — Treat heap fragmentation and stack overflow as design defects (§3 #3 #4).

## Output
A flash/RAM budget per region vs the part's limits, with headroom % and an over-budget flag. See [`../skills/budget-memory/SKILL.md`](../skills/budget-memory/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No device/telemetry PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
