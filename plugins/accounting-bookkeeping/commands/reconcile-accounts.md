---
description: "Reconcile bank and balance-sheet accounts to source before any statement ships. Reach for this first on any reporting question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Reconcile accounts

You are running `/accounting-bookkeeping:reconcile-accounts` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. List the accounts — Every bank/CC/balance-sheet account requiring a tie-out.
2. Tie to source — Match each to an independent statement; investigate variances (§3 #2).
3. Clear reconciling items — Outstanding checks, deposits in transit, timing differences.
4. Gate the report — Don't ship statements until accounts reconcile (§3 #2).

## Output
A reconciliation status gating the report. Traverse Tree 3 in the decision-trees file. See [`../skills/reconcile-accounts/SKILL.md`](../skills/reconcile-accounts/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client financial PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
