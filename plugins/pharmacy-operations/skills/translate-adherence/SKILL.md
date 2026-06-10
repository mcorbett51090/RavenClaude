---
name: translate-adherence
description: "Measure PDC/MPR over the measurement period and translate the adherence band into the star-rating and reimbursement implication. Reach for this on an adherence or star-measure question."
---

# Skill: Translate adherence to stars

An adherence gap is a quality AND a revenue problem at once (§3 #4).

## Step 1 — Measure PDC
Days covered ÷ days in the measurement period via `pharmacy_operations_calc.py adherence` (§3 #4).

## Step 2 — Place the band
Where PDC sits relative to the adherence band threshold (§3 #4).

## Step 3 — Translate to stars/revenue
The star-measure and value-based reimbursement implication of the band (§3 #4).

## Step 4 — Route the clinical
Any drug-therapy question to the licensed pharmacist — never in-team (§3 #8, §2).

## Output
A PDC/adherence-band read with the star-rating and reimbursement implication named. Traverse Tree 3 in the decision-trees file.
