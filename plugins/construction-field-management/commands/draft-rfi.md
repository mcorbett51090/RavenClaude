---
description: "Draft an answerable RFI from a field conflict and log it: one question, drawing/spec references, proposed resolution, cost/schedule-impact flag, needed-by date, and ball-in-court."
argument-hint: "[the field conflict + drawing/spec references + when you need the answer]"
---

You are running `/construction-field-management:draft-rfi`. Use `project-engineer` + the `rfi-and-submittal-workflow` skill.

## Steps
1. State the conflict with the specific drawing/sheet and spec-section references; if intent is ambiguous, name the ambiguity.
2. Ask exactly **one** answerable question (split bundled questions into separate RFIs). Propose a resolution.
3. Flag the cost and schedule impact, and set a needed-by date back-calculated from the activity it gates.
4. Produce the log entry: RFI number, date sent, ball-in-court, needed-by, and the placeholder for date returned + disposition.
5. If the likely answer is scope-bearing, route it to `cost-and-change-controls-lead` to price as a change before it's built; the design answer itself routes to `architecture-aec`.
6. Emit the RFI (use `templates/rfi.md`) + the Structured Output block (with `Field/cost/schedule impact:` and `Ball-in-court:`).
