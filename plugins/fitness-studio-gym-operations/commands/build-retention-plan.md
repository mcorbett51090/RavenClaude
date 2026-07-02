---
description: "Build a member-retention plan: the first-30-days onboarding sequence, an attendance-signal early-warning system, and a cause-first save flow — with the at-risk cohort and expected retention movement named (verify-at-use benchmarks)."
argument-hint: "[studio type + member count + current churn/retention + cancel reasons]"
---

You are running `/fitness-studio-gym-operations:build-retention-plan`. Use `membership-retention-manager` + the `member-onboarding-and-retention` skill.

> Advisory, not financial or medical advice. Churn/LTV/habit-threshold benchmarks are `[verify-at-use]`. No member PII — work in cohorts and attendance signals, never a named member record.

## Steps
1. Capture the baseline: active members, monthly churn/retention curve, top cancel reasons, current onboarding and save tactics (all from the studio's own data).
2. Traverse the **churn-save triage** tree in `knowledge/fitness-studio-decision-trees.md`; cross-check pricing implications against the **membership pricing / tier model** tree.
3. Design the three pieces: (a) the **first-30-days onboarding sequence** to the attendance habit threshold, (b) the **attendance-signal early-warning system** (visits/week trend, days-since-last-visit), (c) the **cause-first save flow** (freeze / downgrade / pause / program-change / graceful let-go — never a reflex discount).
4. Name the at-risk cohort, the expected retention movement, and each owner; flag every benchmark `[verify-at-use]`.
5. Emit using `templates/retention-playbook.md` + the Structured Output block. Escalate P&L/pricing strategy to `fitness-studio-operations-lead`.
