---
name: manage-no-show-flow
description: "Quantify no-show/late-cancel as a flow — lost slots, lost revenue, and the recovery a reminder program delivers. Reach for this on a no-show question."
---

# Skill: Manage no-show flow

A no-show rate without slots-lost and revenue is just a complaint (§3 #1).

## Step 1 — Pull the schedule data
Scheduled visits, no-show/late-cancel rate, avg visit revenue, by clinician and window.

## Step 2 — Quantify the loss
Lost slots × avg visit revenue via `behavioral_health_practice_calc.py no-show` (§3 #1).

## Step 3 — Model the recovery
Apply a reminder-program lift to the no-show rate and re-compute recoverable revenue and slots (§3 #1).

## Step 4 — Add the backfill flow
Waitlist/backfill and telehealth-fill for the residual gap — route telehealth regulatory specifics out (§3 #7).

## Output
A no-show flow read with lost revenue, slots, and reminder-program recovery quantified. Traverse Tree 1 in the decision-trees file.
