---
scenario_id: 2026-06-08-deadline-from-average-not-wcet
contributed_at: 2026-06-08
plugin: embedded-iot-engineering
product: real-time
product_version: "n/a"
scope: likely-general
tags: [real-time, wcet, isr-latency, determinism]
confidence: medium
reviewed: false
---

## Problem

A motor-control loop was signed off because it met its deadline in testing, then jittered and missed under a worst-case interrupt burst. The risk: average-case timing is not a deadline guarantee — a real-time system is correct only if it meets its deadline under worst-case execution and interrupt load (§3 #2).

## Context

- Device: RTOS-based motor controller with a hard control-loop deadline.
- Constraint: deadlines are met on WCET and worst-case ISR latency, and determinism beats throughput on the control path (§3 #2 #4).
- The team reasoned from observed average timing in the lab.

## Attempts

- Tried: **characterized WCET and ISR latency** instead of average timing. Outcome: a rarely-coincident interrupt burst pushed worst-case response past the deadline, invisible in average measurements (§3 #2).
- Tried: **checked schedulability under worst-case load** (rate-monotonic). Outcome: the critical task was unschedulable in the worst case despite passing on average (§3 #2).
- Tried: **removed non-determinism on the path** — a dynamic allocation and a priority inversion. Outcome: bounded worst-case response that held the deadline (§3 #4).

## Resolution

The fix was to **characterize worst-case timing, verify schedulability, and remove non-determinism on the control path** — not to trust average-case lab timing. The output was the WCET/ISR-latency characterization, the schedulability verdict, and the determinism fixes. 

**Action for the next consultant hitting this pattern:** **deadlines are hard constraints — verify on worst case, not average.** Characterize WCET and ISR latency, check worst-case schedulability, and strip dynamic allocation, unbounded blocking, and priority inversion from the control path. See Tree 2 and §3 #2 #4.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
