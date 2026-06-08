---
description: "Design a dual-bank OTA scheme with signed images and automatic rollback before fielding. Reach for this before any device ships."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Plan OTA and rollback

You are running `/embedded-iot-engineering:plan-ota` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Choose the scheme — Dual-bank / A-B images so a bad update never bricks the device (§3 #5).
2. Sign the images — Signed/verified images so only authentic firmware boots (§3 #5).
3. Automate rollback — Boot-confirm watchdog: a failed boot auto-reverts to the known-good bank (§3 #5).
4. Budget the memory — Dual-bank doubles the image footprint — fit it via `embedded_iot_calc.py memory-budget` (§3 #3 #5).

## Output
A dual-bank, signed, auto-rollback OTA design that fits the memory budget, ready before fielding. See [`../skills/plan-ota/SKILL.md`](../skills/plan-ota/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No device/telemetry PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
