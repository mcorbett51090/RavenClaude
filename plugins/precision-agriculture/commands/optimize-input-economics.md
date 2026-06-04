---
description: "Set input rates at the economic optimum where marginal return equals marginal cost, not at agronomic maximum, so the last unit pays. Reach for this on any input decision."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Optimize input economics

You are running `/precision-agriculture:optimize-input-economics` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the response curve — Yield response to the input from data/trials (§3 #1).
2. Find the economic optimum — Where marginal return = marginal cost at current prices.
3. Vary by zone — Apply the optimum by management zone, not field-flat (§3 #2).
4. Quantify the ROI — State the return vs an over/under-applied baseline.

## Output
An economic-optimum rate by zone with the input ROI. See [`../skills/optimize-input-economics/SKILL.md`](../skills/optimize-input-economics/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
