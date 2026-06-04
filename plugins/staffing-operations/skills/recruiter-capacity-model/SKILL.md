---
name: recruiter-capacity-model
description: Right-size a recruiting desk by modeling fillable-order supply against the reqs a recruiter can carry at target conversion, distinguishing nominal from fillable orders and under-fed from under-staffed. Reach for this when the question is whether to hire more recruiters or whether the team is the right size.
---

# Skill: Recruiter capacity model

"Should we hire more recruiters?" is usually the wrong first question — the right one is "are the recruiters we have being fed fillable orders, and are they unblocked?" This skill models capacity honestly.

## Step 1 — Separate nominal orders from fillable orders
Strip dead, on-hold, and structurally-uncompetitive orders. A desk buried in unfillable orders looks understaffed and isn't — adding recruiters to dead demand burns money. Fillable-order count is the only denominator that matters.

## Step 2 — Establish per-recruiter throughput
From the client's own data: reqs a recruiter carries and placements/quarter at the current conversion. Context anchors (`[ESTIMATE]`, Recruiterflow): hires/recruiter/quarter bottomed ~4.5 (early 2023), recovered to ~7.3 (Q1 2026). Use the client's actuals; the benchmark is a sanity rail only.

## Step 3 — Model the gap
Required recruiters = fillable-order supply ÷ (reqs a recruiter can carry at target conversion). Compare to current headcount. The output is over-staffed / right-sized / under-staffed — for the *fillable* demand, not nominal.

## Step 4 — Check the "unblock vs. hire" lever first
Before recommending headcount, check whether existing recruiters are blocked: AI/automation can return up to ~17 hrs/recruiter/week against the ~14.6 hrs/week spent sourcing (Bullhorn GRID 2026, `[ESTIMATE]`). If recruiters are spending capacity on admin a tool could absorb, the cheaper fix is unblocking, not hiring.

## Step 5 — Factor segment difficulty
Credentialing-heavy (healthcare) and academic-calendar-bound (education) desks have lower effective throughput per req — a recruiter on rural school-therapy roles can't carry the same load as one on light-industrial. Adjust the carry assumption by segment, don't average.

## Step 6 — Account for seasonality in the supply curve
Education demand front-loads to spring/summer; healthcare has surge windows. A capacity model on an annual-average order supply will under-staff the peak and over-staff the trough. Model the curve, or at least name the peak the desk must cover.

## Step 7 — State the assumptions to validate
Capacity models are assumption-stacked (carry rate, conversion, fillable %, seasonality). List each assumption and the client data that would confirm it. A model whose assumptions aren't surfaced is a guess with a spreadsheet.

## Reference
Funnel definitions: [`../../knowledge/staffing-kpi-glossary.md`](../../knowledge/staffing-kpi-glossary.md) §A, §D. Decision tree for under-fed vs. under-performing: [`../../knowledge/staffing-decision-trees.md`](../../knowledge/staffing-decision-trees.md).
