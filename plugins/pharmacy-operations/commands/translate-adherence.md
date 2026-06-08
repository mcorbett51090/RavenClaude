---
description: "Measure PDC/MPR over the measurement period and translate the adherence band into the star-rating and reimbursement implication. Reach for this on an adherence or star-measure question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Translate adherence to stars

You are running `/pharmacy-operations:translate-adherence` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure PDC — Days covered ÷ days in the measurement period via `pharmacy_operations_calc.py adherence` (§3 #4).
2. Place the band — Where PDC sits relative to the adherence band threshold (§3 #4).
3. Translate to stars/revenue — The star-measure and value-based reimbursement implication of the band (§3 #4).
4. Route the clinical — Any drug-therapy question to the licensed pharmacist — never in-team (§3 #8, §2).

## Output
A PDC/adherence-band read with the star-rating and reimbursement implication named. Traverse Tree 3 in the decision-trees file. See [`../skills/translate-adherence/SKILL.md`](../skills/translate-adherence/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
