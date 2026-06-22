---
description: "Diagnose and lift the optical capture rate — read the exam-to-optical funnel, find the leak (handoff, quote accuracy, board/menu, lab), and prescribe fixes tied to capture, not markup."
argument-hint: "[capture rate + funnel data + vision-plan mix]"
---

You are running `/optometry-eyecare-practice:review-optical-capture`. Use `optical-dispensary-manager` + the `optical-capture-and-dispensary` skill.

> Advisory operations read. Capture benchmarks are `[ESTIMATE]` / `[verify-at-use]`. No PII/PHI.

## Steps
1. Read the funnel: eyes examined -> Rx written -> Rx filled in your optical -> upgrades captured. Establish the baseline.
2. Traverse the **optical capture-rate improvement** tree in `knowledge/eyecare-practice-decision-trees.md` to locate the leak in order (handoff, then quote accuracy vs the plan, then board/menu fit, then lab).
3. Prescribe the fix tied to capture (not frame markup), with an owner and an expected capture movement; benchmark targets flagged `[ESTIMATE] [verify-at-use]`.
4. Emit using `templates/practice-kpi-dashboard.md` (optical section) + the Structured Output block.
