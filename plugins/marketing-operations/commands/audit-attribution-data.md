---
description: "Audit data hygiene, dedup, and UTM/tracking integrity before trusting any funnel or ROI number. Reach for this first on any new dataset."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Audit attribution data

You are running `/marketing-operations:audit-attribution-data` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Check dedup — Duplicate-lead rate; above a few percent it corrupts funnel and CAC math (§3 #7).
2. Check UTM coverage — Untagged or inconsistently-tagged touches that break attribution (§3 #2).
3. Find orphaned touches — Touch records with no contact/opp linkage.
4. Gate analysis — Don't trust conversion or ROI reads until hygiene clears (§3 #7).

## Output
A data-integrity report gating downstream analysis. Traverse Tree 3 in the decision-trees file. See [`../skills/audit-attribution-data/SKILL.md`](../skills/audit-attribution-data/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No customer/lead PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
