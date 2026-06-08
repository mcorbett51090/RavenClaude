---
description: "Read SLA and backlog as arrivals against resolution capacity — project the days-to-clear. Reach for this on a backlog question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Project backlog

You are running `/customer-support-cx-operations:project-backlog` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure arrivals — Incoming contacts per day for the period.
2. Measure resolution capacity — Contacts the staffed team can resolve per day.
3. Compute the flow — Backlog change = arrivals − capacity via `supportops_calc.py sla-backlog` (§3 #5).
4. Project days-to-clear — Backlog ÷ daily net capacity; if negative, close the gap (§3 #5).

## Output
An arrivals-vs-capacity flow read with backlog change and days-to-clear. Traverse Tree 2 in the decision-trees file. See [`../skills/project-backlog/SKILL.md`](../skills/project-backlog/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
