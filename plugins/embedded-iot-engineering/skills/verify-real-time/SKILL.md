---
name: verify-real-time
description: "Characterize WCET and ISR latency and verify the schedule holds under worst case. Reach for this on any timing or determinism question."
---

# Skill: Verify real-time deadlines

Average-case timing is not a deadline guarantee — only worst-case schedulability is (§3 #2).

## Step 1 — Identify the critical path
The task/ISR with the hard deadline and its worst-case trigger.

## Step 2 — Characterize WCET + ISR latency
Worst-case execution time and interrupt latency, not average (§3 #2).

## Step 3 — Check schedulability
Does the critical task meet its deadline under worst-case load (rate-monotonic/deadline) (§3 #2).

## Step 4 — Remove non-determinism
Kill dynamic allocation, unbounded blocking, priority inversion on the path (§3 #4).

## Output
A worst-case timing characterization with a schedulability verdict naming any at-risk path. Traverse Tree 2 in the decision-trees file.
