---
description: "Design a paved road that is the lowest-friction compliant option, with self-service actions and guardrails. Reach for this on a paved-road question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Design golden path

You are running `/platform-engineering-idp:design-golden-path` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the developer journey — The steps a team takes today, with each ticket and hand-off marked as debt (§3 #4).
2. Pave the easy path — Make the compliant option the lowest-friction one via self-service (§3 #2 #4).
3. Set the guardrails — A policy check on the paved action, not a human ticket (§3 #4).
4. Decide pave vs mandate — Pave unless impossible; quantify removed toil via `platform_engineering_idp_calc.py toil`.

## Output
A golden-path design that is the easy compliant option, with guardrails and removed toil named. Traverse Tree 2 in the decision-trees file. See [`../skills/design-golden-path/SKILL.md`](../skills/design-golden-path/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No internal credentials/PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
