---
name: classify-dora
description: "Compute the four DORA keys and classify the org against the bands with windows and baselines. Reach for this on a DevEx-measurement question."
---

# Skill: Classify DORA

'Developers are happier' is not a metric (§3 #3).

## Step 1 — Pull the four keys
Deploy frequency, lead time for change, change-failure rate, MTTR over a fixed window.

## Step 2 — Classify each
Map each key to elite/high/medium/low via `platform_engineering_idp_calc.py dora` (§3 #3).

## Step 3 — Attach windows + baselines
Every key carries a window and a prior baseline, or it doesn't ship (§3 #3).

## Step 4 — Name the binding constraint
The weakest key is the lever; pair it with survey signal, not instead of it.

## Output
A classified four-key DORA read with windows, baselines, and the binding constraint named. Traverse Tree 1 in the decision-trees file.
