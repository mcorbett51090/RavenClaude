---
description: "Read an engagement survey segmented — surface the team/tenure/manager pockets a company-wide eNPS hides and tie them to forward attrition risk. Reach for this on an engagement-survey question."
argument-hint: "[the situation, e.g. the survey / segment / cohort in question]"
---

# Read engagement signals

You are running `/people-operations-hr:read-engagement-signals` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Segment first — break eNPS / favorability by team, tenure cohort, and manager (§3 #4).
2. Find the at-risk pocket — localize the low-favorability segment a company average hides.
3. Tie to attrition risk — cross the pocket against regretted-attrition trend.
4. Isolate manager quality — team-level deltas separate the manager/span effect (§3 #7).

## Output
A segmented engagement read naming the at-risk pockets, the manager/span effects, and the forward attrition risk. See [`../skills/read-engagement-signals/SKILL.md`](../skills/read-engagement-signals/SKILL.md) and [`../knowledge/people-ops-kpi-glossary.md`](../knowledge/people-ops-kpi-glossary.md).

## Guardrails
- Apply the §3 house opinions before any method; read segmented, never company-wide.
- No employee PII in the output; cite a source + date for every external benchmark (or mark it).
- End with owner / date / expected movement on each recommendation.
