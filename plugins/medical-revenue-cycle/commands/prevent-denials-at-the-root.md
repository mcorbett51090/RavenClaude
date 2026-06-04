---
description: "Categorize denials by root cause and owner and push fixes upstream to registration and authorization, instead of only appealing. Reach for this when the denial rate is high."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Prevent denials at the root

You are running `/medical-revenue-cycle:prevent-denials-at-the-root` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Categorize by root cause — Split denials into eligibility, authorization, coding, documentation, and timely-filing (§3 #5).
2. Assign the owner — Each category has an owner — front desk, coder, or biller (§3 #6).
3. Fix upstream — Push eligibility/auth fixes to scheduling and registration where most denials are born (§3 #6).
4. Track prevented denials — Measure the denial rate toward <5% and quantify prevented rework (§3 #1).

## Output
A root-cause-categorized denial map, owners, upstream fixes, and the prevented-denial impact. See [`../skills/prevent-denials/SKILL.md`](../skills/prevent-denials/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
