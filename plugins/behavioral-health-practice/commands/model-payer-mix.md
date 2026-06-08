---
description: "Read reimbursement net of variable cost by payer, compute blended margin, and model a mix shift — flagging parity for counsel. Reach for this on a payer or margin question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Model payer mix and margin

You are running `/behavioral-health-practice:model-payer-mix` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull per-payer data — Visit volume, reimbursement, and variable cost per visit by payer.
2. Compute blended margin — Blended reimbursement and margin via `behavioral_health_practice_calc.py payer-mix` (§3 #5).
3. Model the shift — New blend vs current blend → mix-shift delta, with capacity caveats (§3 #4 #5).
4. Flag parity — Parity gaps where behavioral-health rates lag — route the determination to counsel (§3 #5 #8).

## Output
A per-payer margin read with the blended figure, mix-shift delta, and parity flagged to counsel. See [`../skills/model-payer-mix/SKILL.md`](../skills/model-payer-mix/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
