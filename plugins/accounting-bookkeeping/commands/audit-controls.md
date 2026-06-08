---
description: "Audit segregation of duties and chart-of-accounts hygiene before trusting the books. Reach for this on a controls or data-quality question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Audit controls

You are running `/accounting-bookkeeping:audit-controls` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map SoD — Who approves, enters, reconciles — separation or compensating controls (§3 #5).
2. Check approval thresholds — Payment-approval limits and exceptions.
3. Audit the COA — Duplicates, catch-alls, inconsistent coding (§3 #7).
4. Gate analysis — Don't trust reports until controls and COA are sound (§3 #5 #7).

## Output
A controls + COA-hygiene read gating downstream analysis. See [`../skills/audit-controls/SKILL.md`](../skills/audit-controls/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
