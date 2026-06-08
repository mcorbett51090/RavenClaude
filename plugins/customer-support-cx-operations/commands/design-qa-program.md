---
description: "Design a statistically meaningful QA sampling program and a tier/escalation model. Reach for this on a quality or routing question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Design QA program

You are running `/customer-support-cx-operations:design-qa-program` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Set the sampling goal — Detect real quality variation by agent/queue (§3 #6).
2. Size the sample — Enough scored contacts per agent/queue to be meaningful (§3 #6).
3. Design the rubric — Tied to FCR and CSAT outcomes, not subjective taste (§3 #4).
4. Design tiering — Route simple vs complex; not all-omni (§3 #7).

## Output
A QA sampling design and tier/escalation model tied to outcomes. See [`../skills/design-qa-program/SKILL.md`](../skills/design-qa-program/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
