---
name: read-revpar
description: "Read RevPAR as ADR × occupancy and test the rate-vs-occupancy trade-off; carry to GOPPAR if profit is given. Reach for this on a rate or RevPAR question."
---

# Skill: Read RevPAR

Chasing occupancy by cutting rate, or rate into empty rooms, both leave RevPAR on the table (§3 #1).

## Step 1 — Set the room base
Rooms available and rooms sold for the period.

## Step 2 — Compute RevPAR
Occupancy, ADR, and RevPAR via `hotel_hospitality_operations_calc.py revpar` (§3 #1).

## Step 3 — Test the trade-off
Does a rate change lift or erode the product against the demand curve (§3 #1).

## Step 4 — Carry to GOPPAR
If total revenue + GOP given, compute GOPPAR — profit beats top line (§3 #5).

## Output
A RevPAR (and optional GOPPAR) read with the rate-vs-occupancy trade-off named. Traverse Tree 1 in the decision-trees file.
