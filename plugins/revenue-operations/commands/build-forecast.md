---
description: "Select and implement a forecast methodology (weighted probability, commit/category, or AI-assisted), calibrate stage probabilities, design the coverage calculation and sales-velocity metric, and produce a forecast rollup protocol."
argument-hint: "[context, e.g. 'commit/category model, enterprise AEs, Salesforce CRM, Q3 close, $4M quota remaining, current pipeline $9M']"
---

You are running `/revenue-operations:build-forecast`. Use the `pipeline-forecast-engineer`
discipline and the `forecasting-methodology` skill.

## Steps

1. Assess data and process maturity: CRM data quality (stage age distribution, required-field
   completeness), activity capture (manual vs. auto via Gong/Outreach), historical data volume
   (months of closed deals), and rep forecast discipline. Use the maturity rubric in the skill.

2. Traverse the forecast-method decision tree in `knowledge/revops-decision-trees.md` to select
   the methodology. Name the leaf node reached and the reason it was selected over alternatives.

3. Design the methodology:
   - **Weighted probability**: pull stage probabilities; flag any that are vendor defaults and
     need calibration. Calculate weighted forecast using `scripts/revops_calc.py` (weighted-forecast
     mode). Show the top 10 deals by weighted value.
   - **Commit/category**: design the bucket definitions, rep accountability rules, manager
     overlay protocol, and the commit-accuracy tracking mechanism.
   - **AI-assisted**: run the readiness checklist (CRM quality, activity capture, data volume);
     recommend tooling only if prerequisites are met [verify tool pricing/availability-at-use].

4. Calculate pipeline coverage: open pipeline ÷ remaining quota gap using `scripts/revops_calc.py`
   (pipeline-coverage mode). State the win-rate used; flag if using estimated win-rate vs.
   historical.

5. Calculate sales velocity: (#opps × win-rate × ACV) ÷ cycle-length using the calculator.
   Produce the metric by segment if deal data is segmented.

6. Design the forecast rollup protocol: what each level (AE → Manager → VP → CRO) adds, the
   cadence, and the data that must be current in the CRM before the meeting.

7. Emit the Structured Output block; hand the CRM implementation to `crm-operations-architect`,
   the quota-coverage sizing to `sales-comp-and-territory-analyst`, and governance to `revops-lead`.
