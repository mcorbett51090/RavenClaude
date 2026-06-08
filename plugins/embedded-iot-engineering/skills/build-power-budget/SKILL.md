---
name: build-power-budget
description: "Build the duty-cycled current profile and compute average current and battery life. Reach for this on any battery-life or energy question."
---

# Skill: Build power budget

A battery-life number from active current alone ignores the sleep floor and over-promises by a wide margin (§3 #1).

## Step 1 — Profile the states
Active mA and sleep mA from the datasheet (dated) and the duty cycle (active vs sleep fraction) (§3 #1 #8).

## Step 2 — Compute average current
Active mA × active fraction + sleep mA × sleep fraction via `embedded_iot_calc.py power-budget` (§3 #1).

## Step 3 — Derive battery life
Capacity (mAh) ÷ average current, derated for self-discharge/EOL (§3 #1).

## Step 4 — Name the dominant sink
Usually the sleep floor or the radio TX burst — then duty-cycle it down (§3 #1).

## Output
An average-current and battery-life estimate from the duty-cycled profile, with the dominant sink named. Traverse Tree 1 in the decision-trees file.
