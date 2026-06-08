---
name: size-throughput-staffing
description: "Size technician and pharmacist hours against script volume PLUS clinical-service time, holding verification safety as the constraint. Reach for this on a throughput or staffing question."
---

# Skill: Size throughput and staffing

A throughput plan that erodes verification time is a safety failure, not a gain (§3 #1).

## Step 1 — Measure the volume
Daily script volume and the clinical-service time load (§3 #5).

## Step 2 — Compute the hours
Tech and pharmacist hours via `pharmacy_operations_calc.py throughput-staffing` (§3 #5).

## Step 3 — Hold safety as the constraint
Verification capacity must cover fill volume — never trade it for speed (§3 #1).

## Step 4 — Name the gap
Hours needed vs current, with the verification-safety gap flagged (§3 #1).

## Output
A staffing read covering volume + clinical time with the verification-safety constraint held. Traverse Tree 1 in the decision-trees file.
