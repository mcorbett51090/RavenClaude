---
name: estimate-bad-debt
description: "Estimate bad-debt from AR aging buckets weighted by loss rate. Reach for this on a receivables-risk question."
---

# Skill: Estimate bad debt

Older buckets carry sharply higher loss rates (§3 #3).

## Step 1 — Bucket the AR
Current / 30 / 60 / 90+ aging buckets (§3 #3).

## Step 2 — Apply loss rates
Per-bucket expected loss; older = higher.

## Step 3 — Weight the estimate
Σ(bucket × loss rate) via `acctgops_calc.py aging` (§3 #3).

## Step 4 — Route the write-off
Tax treatment of write-offs → a licensed CPA (§2 #8).

## Output
A weighted bad-debt estimate from the aging.
