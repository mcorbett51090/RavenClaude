---
name: size-staffing
description: "Size agents from workload and a target occupancy band — not a fixed agent:ticket ratio. Reach for this on a staffing question."
---

# Skill: Size staffing

A fixed ratio over- or under-staffs the moment volume varies (§3 #2).

## Step 1 — Forecast volume by interval
Contacts per interval and handle time (AHT).

## Step 2 — Compute workload hours
Contacts × AHT per interval.

## Step 3 — Staff to occupancy
Agents = workload ÷ (interval hours × target occupancy) via `supportops_calc.py staffing` (§3 #2).

## Step 4 — Sanity-check the band
Occupancy too high burns out; too low wastes cost (§3 #2).

## Output
A workload/occupancy staffing model with the target band stated.
