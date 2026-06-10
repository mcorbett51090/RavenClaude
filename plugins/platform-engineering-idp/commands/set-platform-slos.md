---
description: "Define platform SLIs/SLOs and an error budget that gates platform change. Reach for this on a platform-reliability question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Set platform SLOs

You are running `/platform-engineering-idp:set-platform-slos` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pick the SLIs — Paved-path success rate, provisioning p95 latency, pipeline reliability.
2. Set the SLO targets — Targets carry a source + date or an unverified mark (§3 #6 #8).
3. Compute the error budget — (1 − target) × window; it gates how much change ships (§3 #6).
4. Gate change on the budget — Freeze platform features when the budget is spent — same as any service (§3 #6).

## Output
A platform SLO set with an error budget that gates change. Traverse Tree 3 in the decision-trees file. See [`../skills/set-platform-slos/SKILL.md`](../skills/set-platform-slos/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No internal credentials/PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
