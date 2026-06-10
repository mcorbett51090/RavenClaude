---
description: "Design a group benefits program as a system: plan design per line, a funding recommendation (fully-insured vs self-funded vs level-funded), contribution structure, and the ACA/ERISA obligations triggered — educational, not advice."
argument-hint: "[group size + workforce profile + budget + current coverage/pain]"
---

You are running `/insurance-life-health-benefits:design-benefits-program`. Use `benefits-advisor` + the `benefits-plan-design` skill.

## Steps
1. Map the workforce: size, age/family mix, income, how they use care, and the budget. Name the cognitive/financial trade-offs that matter for this population.
2. Design the package per line — medical (HMO/PPO/HDHP+HSA mechanics), dental, vision, group life + AD&D, short- and long-term disability. Flag any coverage gap (especially disability income).
3. Recommend a funding model (fully-insured vs self-funded vs level-funded) sized to the group, with the conditions that would change the call. Never self-fund just to dodge a renewal.
4. Set the contribution/eligibility structure and check ACA affordability + minimum value; name the ALE/ERISA/SPD obligations triggered (`[verify-at-build]` the current-year thresholds).
5. Route: rate adequacy → underwriting-and-actuarial-analyst; enrollment + filings → enrollment-and-compliance-lead; HR administration → people-ops-hr.
6. Emit the benefits-program brief + the Structured Output block (with `Not advice:` and `Coverage gaps flagged:`). Restate the educational framing and name the broker/ERISA-counsel sign-off.
