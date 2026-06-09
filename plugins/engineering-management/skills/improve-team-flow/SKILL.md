---
name: improve-team-flow
description: "Diagnose why delivery is unpredictable using flow + DORA as system signals, find the constraint, and fix it — never by velocity-quota'ing people. Reach for this when dates keep slipping."
---

# Skill: Improve team flow

Measure flow and outcomes, never lines or commits — and never rank a person by a velocity metric (§3 #3).

## Step 1 — Measure, don't guess
Pull lead time, WIP, change-fail, and MTTR as **system** signals with a baseline (§3 #3). A signal without a window + baseline is just a number.

## Step 2 — Find where time goes
High WIP / context-switching? Hidden rework? Blocked dependencies? Estimation/scope churn? Traverse Tree 2 to localize the constraint.

## Step 3 — Fix the constraint
Limit WIP and shrink batch size (Little's Law); make dependencies visible; tighten estimation hygiene. More pressure on a leaking process wastes the team.

## Step 4 — Check the people cost
If the candidate fix is "push harder," STOP — that's a velocity crackdown, not a system fix (§3 #3). Check on-call/burnout load with `oncall-load`.

## Output
A flow diagnosis with the constraint named and a sustainable fix, owners + dates attached. Route the people/burnout impact to `people-and-growth-manager`, tech-debt-as-constraint to `technical-health-manager`.
