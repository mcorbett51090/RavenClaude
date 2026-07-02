---
description: "Build an early-alert / at-risk retention intervention plan for a cohort: read persistence with its definition, triage by leverage, and target the high-DFW gateway courses (verify-at-use; no student PII)."
argument-hint: "[cohort + term + retention numbers + early-alert / at-risk signals + DFW courses]"
---

You are running `/higher-education-administration:build-retention-plan`. Use `student-success-advisor` + the `retention-and-student-success` skill.

> Advisory, not academic-policy or clinical advice. Retention/persistence metrics carry a definition + `[verify-at-use]`. **Cohort-level and risk-segment only — no student PII;** individual data stays in the early-alert/SIS system.

## Steps
1. Capture the cohort and attach the **definition** (cohort, term, source) to every retention/persistence number.
2. Traverse the **at-risk student triage** tree in `knowledge/higher-ed-decision-trees.md`.
3. Segment the loss (or the at-risk cohort) by cause and term; triage into intervention tiers **by leverage, not alarm**.
4. Read the high-DFW gateway courses feeding the loss — name the course-level fix, not just the student touch.
5. Check whether the loss is an enrollment-quality signal; if so, flag it to `enrollment-management-strategist`.
6. Emit using `templates/retention-intervention-plan.md` + the Structured Output block.
