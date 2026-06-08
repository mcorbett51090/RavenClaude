---
description: "Rank audit issues by user-impact and effort into a sequenced remediation plan with owners. Reach for this when there are more fixes than time."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Prioritize remediation

You are running `/accessibility-engineering:prioritize-remediation` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Inventory the issues — Each with WCAG criterion, severity, user-impact, and a rough effort estimate.
2. Score impact and effort — Rank by user-impact ÷ effort via `accessibility_calc.py remediation`.
3. Separate blockers from polish — Level-A blockers and high-impact quick wins first (§3 #7).
4. Sequence with owners — A roadmap with owners, dates, and expected conformance/impact movement.

## Output
A remediation plan ranked by impact and effort, with blockers, quick wins, and owners. Traverse Tree 2 in the decision-trees file. See [`../skills/prioritize-remediation/SKILL.md`](../skills/prioritize-remediation/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
