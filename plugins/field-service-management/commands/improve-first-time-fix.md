---
description: "Diagnose a below-target first-time-fix rate — segment failures by root cause (parts/skill/diagnosis/information), rank the improvement opportunities, and produce a prioritized action plan routing each category to the right specialist."
argument-hint: "[context, e.g. 'first-time-fix at 63%, 15 techs, HVAC+plumbing, no structured root-cause tracking']"
---

You are running `/field-service-management:improve-first-time-fix`. Use the
`technician-productivity-analyst` discipline and the `technician-productivity-and-first-time-fix`
skill.

## Steps

1. Establish the current first-time-fix rate baseline using `scripts/fsm_calc.py`
   `first_time_fix_rate()`. If raw data is provided, compute it; if only an anecdotal rate is
   given, note the data-quality assumption.

2. Validate the underlying job-completion data: are failure codes captured on every job? Are
   technicians logging actual close times or is dispatch bulk-closing? Flag data-quality issues
   before drawing conclusions.

3. Segment first-time-fix failures into root-cause categories:
   - Parts unavailable (part not on truck, not pre-pulled)
   - Skill/cert mismatch (tech dispatched outside authorization)
   - Misdiagnosis (wrong component identified)
   - Incomplete job information (symptom or history missing at dispatch)
   - Customer expectation mismatch (scope not confirmed at booking)

   Calculate the % of failures in each category. Rank by share.

4. For each category, identify the fix owner:
   - Parts → `parts-and-inventory-analyst` (truck-stock or pre-pull redesign)
   - Skill/dispatch → `dispatch-and-scheduling-engineer` (skill-match enforcement)
   - Diagnosis/training → coaching plan (this agent owns)
   - Information/data → mobile workflow / job-intake triage improvement
   - Customer expectation → booking SOP change

5. Quantify the opportunity: for the top 2 root-cause categories, estimate the first-time-fix
   rate gain if that category were eliminated. Prioritize the highest-gain, lowest-effort fix first.

6. Produce the action plan: one action per root-cause category, with owner, timeline, and the
   measurement that confirms it's working (e.g., parts-delay failures down 50% in 60 days).

7. Emit the Structured Output block with handoffs to `parts-and-inventory-analyst` and
   `dispatch-and-scheduling-engineer` for the non-skill categories.
