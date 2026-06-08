---
description: "Build the duty-cycled current profile and compute average current and battery life. Reach for this on any battery-life or energy question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build power budget

You are running `/embedded-iot-engineering:build-power-budget` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Profile the states — Active mA and sleep mA from the datasheet (dated) and the duty cycle (active vs sleep fraction) (§3 #1 #8).
2. Compute average current — Active mA × active fraction + sleep mA × sleep fraction via `embedded_iot_calc.py power-budget` (§3 #1).
3. Derive battery life — Capacity (mAh) ÷ average current, derated for self-discharge/EOL (§3 #1).
4. Name the dominant sink — Usually the sleep floor or the radio TX burst — then duty-cycle it down (§3 #1).

## Output
An average-current and battery-life estimate from the duty-cycled profile, with the dominant sink named. Traverse Tree 1 in the decision-trees file. See [`../skills/build-power-budget/SKILL.md`](../skills/build-power-budget/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No device/telemetry PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
