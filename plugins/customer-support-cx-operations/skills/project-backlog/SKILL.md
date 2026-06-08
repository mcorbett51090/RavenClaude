---
name: project-backlog
description: "Read SLA and backlog as arrivals against resolution capacity — project the days-to-clear. Reach for this on a backlog question."
---

# Skill: Project backlog

Backlog grows whenever arrivals exceed capacity; exhortation doesn't fix flow (§3 #5).

## Step 1 — Measure arrivals
Incoming contacts per day for the period.

## Step 2 — Measure resolution capacity
Contacts the staffed team can resolve per day.

## Step 3 — Compute the flow
Backlog change = arrivals − capacity via `supportops_calc.py sla-backlog` (§3 #5).

## Step 4 — Project days-to-clear
Backlog ÷ daily net capacity; if negative, close the gap (§3 #5).

## Output
An arrivals-vs-capacity flow read with backlog change and days-to-clear. Traverse Tree 2 in the decision-trees file.
