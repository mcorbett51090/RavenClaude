---
description: "Characterize WCET and ISR latency and verify the schedule holds under worst case. Reach for this on any timing or determinism question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Verify real-time deadlines

You are running `/embedded-iot-engineering:verify-real-time` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Identify the critical path — The task/ISR with the hard deadline and its worst-case trigger.
2. Characterize WCET + ISR latency — Worst-case execution time and interrupt latency, not average (§3 #2).
3. Check schedulability — Does the critical task meet its deadline under worst-case load (rate-monotonic/deadline) (§3 #2).
4. Remove non-determinism — Kill dynamic allocation, unbounded blocking, priority inversion on the path (§3 #4).

## Output
A worst-case timing characterization with a schedulability verdict naming any at-risk path. Traverse Tree 2 in the decision-trees file. See [`../skills/verify-real-time/SKILL.md`](../skills/verify-real-time/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No device/telemetry PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
