---
scenario_id: 2026-06-08-battery-life-from-active-only
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: power
product_version: "n/a"
scope: likely-general
tags: [power-budget, duty-cycle, sleep-current, battery-life]
confidence: medium
reviewed: false
---

## Problem

A team quoted a multi-year battery life by dividing capacity by the active current, then field units died in weeks. The risk: battery life is set by average current over the duty cycle, and an estimate that ignores the sleep floor and wake frequency over-promises massively — the power budget is the spec, not an afterthought (§3 #1).

## Context

- Device: battery-powered sensor on a coin cell, mostly asleep.
- Constraint: average current = active mA × active fraction + sleep mA × sleep fraction, and the sleep floor usually dominates a long-life budget (§3 #1).
- The team reasoned from the active-mode current only.

## Attempts

- Tried: **built the duty-cycled profile** via `embedded_iot_calc.py power-budget` before trusting the estimate. Outcome: the sleep-mode current was far higher than assumed — a peripheral was left clocked, swamping the budget (§3 #1).
- Tried: **decomposed by state** to find the dominant sink. Outcome: the sleep floor, not the active burst, set the battery life — the original estimate ignored it entirely (§3 #1).
- Tried: **deepened the sleep state** (gated the peripheral clock) and re-computed against the datasheet figures, dated and bench-measured. Outcome: average current dropped to the design target (§3 #1 #8).

## Resolution

The fix was to **build the power budget first, find and cut the dominant sleep-floor sink, and verify on the bench** — not to quote battery life from active current. The output was the duty-cycled profile, the dominant-sink call, and a measured average current. The firmware sleep fix routed to the firmware specialist (§3 #4).

**Action for the next consultant hitting this pattern:** **the power budget is the spec — compute average current over the duty cycle, never from active current alone.** The sleep floor and wake rate usually dominate; build the profile first and bench-verify the datasheet figures. See Tree 1 and the `power-budget` mode (§3 #1 #8).

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
