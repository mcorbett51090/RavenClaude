---
name: set-platform-slos
description: "Define platform SLIs/SLOs and an error budget that gates platform change. Reach for this on a platform-reliability question."
---

# Skill: Set platform SLOs

The platform is production for its developer-customers (§3 #6).

## Step 1 — Pick the SLIs
Paved-path success rate, provisioning p95 latency, pipeline reliability.

## Step 2 — Set the SLO targets
Targets carry a source + date or an unverified mark (§3 #6 #8).

## Step 3 — Compute the error budget
(1 − target) × window; it gates how much change ships (§3 #6).

## Step 4 — Gate change on the budget
Freeze platform features when the budget is spent — same as any service (§3 #6).

## Output
A platform SLO set with an error budget that gates change. Traverse Tree 3 in the decision-trees file.
