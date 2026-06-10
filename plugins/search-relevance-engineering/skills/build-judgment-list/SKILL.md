---
name: build-judgment-list
description: "Build graded relevance judgments (explicit or click-derived) and an offline harness before tuning. Reach for this when there's no eval."
---

# Skill: Build judgment list

Tuning without a judgment list is guessing dressed as engineering (§3 #3).

## Step 1 — Sample the query mix
Representative queries weighted by real traffic (§3 #7).

## Step 2 — Grade relevance
Explicit graded labels or click-derived judgments, with position-bias caution (§3 #3 #6).

## Step 3 — Build the offline harness
Reusable NDCG/MRR/precision@k harness over the judgment list (§3 #3).

## Step 4 — Set the baseline
The current ranking's metrics — the bar every change must beat (§3 #1).

## Output
A graded judgment list and an offline harness with a recorded baseline.
