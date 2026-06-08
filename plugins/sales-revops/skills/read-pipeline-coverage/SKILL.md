---
name: read-pipeline-coverage
description: "Read coverage as a ratio against quota by segment and close-date, not a total pipeline number. Reach for this on a coverage question."
---

# Skill: Read pipeline coverage

A pipeline total without its quota is meaningless (§3 #1).

## Step 1 — Set the quota baseline
Remaining quota by segment and period.

## Step 2 — Compute coverage
Open pipeline ÷ remaining quota via `revops_calc.py coverage`.

## Step 3 — Segment it
Coverage by segment and close-date; a healthy aggregate can hide a short segment (§3 #1).

## Step 4 — Compare to target ratio
Against the segment's historical win-rate-implied coverage need.

## Output
A segmented coverage read vs target ratio, naming the short segments.
