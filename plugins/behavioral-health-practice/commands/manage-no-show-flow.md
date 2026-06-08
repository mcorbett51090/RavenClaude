---
description: "Quantify no-show/late-cancel as a flow — lost slots, lost revenue, and the recovery a reminder program delivers. Reach for this on a no-show question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Manage no-show flow

You are running `/behavioral-health-practice:manage-no-show-flow` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull the schedule data — Scheduled visits, no-show/late-cancel rate, avg visit revenue, by clinician and window.
2. Quantify the loss — Lost slots × avg visit revenue via `behavioral_health_practice_calc.py no-show` (§3 #1).
3. Model the recovery — Apply a reminder-program lift to the no-show rate and re-compute recoverable revenue and slots (§3 #1).
4. Add the backfill flow — Waitlist/backfill and telehealth-fill for the residual gap — route telehealth regulatory specifics out (§3 #7).

## Output
A no-show flow read with lost revenue, slots, and reminder-program recovery quantified. Traverse Tree 1 in the decision-trees file. See [`../skills/manage-no-show-flow/SKILL.md`](../skills/manage-no-show-flow/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
