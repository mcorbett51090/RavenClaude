---
description: "Stress-test eligibility criteria against the addressable population and site capacity before the protocol locks, since restrictive criteria are the biggest enrollment killer. Reach for this at design."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Stress-test protocol feasibility

You are running `/clinical-trials:stress-test-protocol-feasibility` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map eligibility to population — Estimate the enrollable pool after each inclusion/exclusion criterion (§3 #1).
2. Find the criteria that shrink the pool — Flag the high-cost criteria and whether they're scientifically necessary.
3. Check site capacity — Match the pool to realistic site enrollment rates.
4. Recommend, as decision-support — Propose criteria adjustments for the medical team to weigh.

## Output
An eligibility-vs-population read, the pool-shrinking criteria, a site-capacity check, and decision-support recommendations. See [`../skills/stress-test-feasibility/SKILL.md`](../skills/stress-test-feasibility/SKILL.md). Traverse the matching tree in [`../knowledge/trials-decision-trees.md`](../knowledge/trials-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
