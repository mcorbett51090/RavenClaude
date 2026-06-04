---
description: "Decompose a loss-ratio move into frequency and severity, since they have opposite responses, before prescribing. Reach for this when the loss ratio moves."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Separate frequency from severity

You are running `/insurance-pc:separate-frequency-from-severity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Split the loss ratio — Claim count (frequency) vs cost per claim (severity) (§3 #3).
2. Attribute severity — Social inflation, mix shift, or reserve strengthening.
3. Attribute frequency — Risk selection, exposure growth, or external trend.
4. Match the response — Risk-selection fix for frequency; pricing/claims fix for severity.

## Output
A frequency/severity split, an attribution of each, and the matched response. See [`../skills/separate-frequency-and-severity/SKILL.md`](../skills/separate-frequency-and-severity/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
