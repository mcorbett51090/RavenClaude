---
name: compute-real-margin
description: "Compute reimbursement minus acquisition cost minus DIR fees per script and flag negative-margin scripts the sticker hid. Reach for this on a margin question."
---

# Skill: Compute real margin after DIR

The sticker reimbursement overstates margin; DIR can flip a script negative (§3 #3).

## Step 1 — Pull the per-script data
Reimbursement, acquisition cost, and DIR/clawback fee per script.

## Step 2 — Compute real margin
Reimbursement − acquisition − DIR via `pharmacy_operations_calc.py margin` (§3 #3).

## Step 3 — Flag the negatives
Scripts negative after DIR and the classes driving them (§3 #3).

## Step 4 — Handle specialty distinctly
Specialty/340B/refrigerated priced separately (§3 #6).

## Output
A per-script real-margin read net of DIR with negative-margin scripts flagged. Traverse Tree 2 in the decision-trees file.
