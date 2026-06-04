---
description: "Read practice revenue as production per DVM and average client transaction × visits, never one alone, so a revenue problem is diagnosed correctly. Reach for this on any revenue question."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Instrument production and ACT

You are running `/veterinary-practice:instrument-production-and-act` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute production per DVM — Total production ÷ doctor-FTEs, by doctor (§3 #2).
2. Compute ACT and visits — Average client transaction × visit volume — the other half of revenue.
3. Decompose a revenue move — Attribute a change to doctors, production-per-doctor, ACT, or visits — each has a different fix.
4. Baseline it — Every figure carries a window and a baseline (§3 #1).

## Output
A two-engine revenue decomposition with the driver of any move named and baselined. See [`../skills/instrument-production-and-act/SKILL.md`](../skills/instrument-production-and-act/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
