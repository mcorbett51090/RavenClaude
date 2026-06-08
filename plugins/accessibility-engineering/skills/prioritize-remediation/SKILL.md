---
name: prioritize-remediation
description: "Rank audit issues by user-impact and effort into a sequenced remediation plan with owners. Reach for this when there are more fixes than time."
---

# Skill: Prioritize remediation

A flat issue list with no priority leaves the team fixing cosmetics while a Level-A blocker ships (§3 #7).

## Step 1 — Inventory the issues
Each with WCAG criterion, severity, user-impact, and a rough effort estimate.

## Step 2 — Score impact and effort
Rank by user-impact ÷ effort via `accessibility_calc.py remediation`.

## Step 3 — Separate blockers from polish
Level-A blockers and high-impact quick wins first (§3 #7).

## Step 4 — Sequence with owners
A roadmap with owners, dates, and expected conformance/impact movement.

## Output
A remediation plan ranked by impact and effort, with blockers, quick wins, and owners. Traverse Tree 2 in the decision-trees file.
