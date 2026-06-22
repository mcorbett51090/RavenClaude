---
description: "Plan a recall/recare campaign off the patient base by exam type — intervals, cohorts, cadence, and a capacity check — to fill the schedule."
argument-hint: "[practice + soft cohorts + open capacity]"
---

You are running `/optometry-eyecare-practice:plan-recall`. Use `practice-operations-lead` + the `schedule-and-recall-management` skill.

> Recall *intervals* are clinical-protocol decisions — `[verify-at-use]`. No PII/PHI — cohorts and counts, never patient records.

## Steps
1. Identify the cohorts by exam type and the recall interval each carries (per clinical protocol — verify-at-use).
2. Traverse the **recall cadence by exam type** tree in `knowledge/eyecare-practice-decision-trees.md`.
3. Confirm the schedule is genuinely soft (fill rate, not a capacity ceiling) before launching — capacity = lanes × slots × fill rate.
4. Build the cadence (touch sequence, channels, window) and the reactivation target vs baseline.
5. Emit using `templates/recall-campaign-plan.md` + the Structured Output block.
