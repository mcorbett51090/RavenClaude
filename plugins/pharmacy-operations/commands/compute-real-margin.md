---
description: "Compute reimbursement minus acquisition cost minus DIR fees per script and flag negative-margin scripts the sticker hid. Reach for this on a margin question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Compute real margin after DIR

You are running `/pharmacy-operations:compute-real-margin` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull the per-script data — Reimbursement, acquisition cost, and DIR/clawback fee per script.
2. Compute real margin — Reimbursement − acquisition − DIR via `pharmacy_operations_calc.py margin` (§3 #3).
3. Flag the negatives — Scripts negative after DIR and the classes driving them (§3 #3).
4. Handle specialty distinctly — Specialty/340B/refrigerated priced separately (§3 #6).

## Output
A per-script real-margin read net of DIR with negative-margin scripts flagged. Traverse Tree 2 in the decision-trees file. See [`../skills/compute-real-margin/SKILL.md`](../skills/compute-real-margin/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No patient PHI in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
