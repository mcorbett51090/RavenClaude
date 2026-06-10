---
name: size-labor
description: "Size labor to the occupancy forecast by hours-per-occupied-room and protect flow-through. Reach for this on a labor question."
---

# Skill: Size labor

Staffing a fixed roster regardless of occupancy over-spends low nights (§3 #4).

## Step 1 — Set occupied rooms
Forecast occupied rooms for the period.

## Step 2 — Apply the labor standard
Occupied rooms × target hours-per-occupied-room via `hotel_hospitality_operations_calc.py labor` (§3 #4).

## Step 3 — Compute cost per occupied room
Labor cost ÷ occupied rooms — the productivity number.

## Step 4 — Protect flow-through
Balance the cut against GOPPAR and service level (§3 #4 #5).

## Output
A labor-hours and cost-per-occupied-room read flexed to the forecast. Traverse Tree 2 in the decision-trees file.
