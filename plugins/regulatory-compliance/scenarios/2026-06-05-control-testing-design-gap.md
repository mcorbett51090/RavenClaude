---
scenario_id: 2026-06-05-control-testing-design-gap
contributed_at: 2026-06-05
plugin: regulatory-compliance
product: control-testing
product_version: "n/a"
scope: likely-general
tags: [control-testing, design-effectiveness, detective, remediation, three-lines]
confidence: medium
reviewed: false
---

## Problem

A second-line compliance team was about to report a control as "effective" after a sample-based operating-effectiveness test passed (25 of 25 samples clean). The control was a **detective** reconciliation that was supposed to catch a specific exception type — but the team had never confirmed the control was *designed* to catch that exception in the first place. They had tested whether the control ran consistently, not whether the control, even when run perfectly, *would* detect the thing it existed to detect. `risk-and-controls-specialist` was asked to review the test before the result went into the control self-assessment.

## Context

- Sector: regulated financial institution running a compliance control self-assessment (the same design-before-operating distinction applies to any controls-assurance context — SOC, internal audit, regulator exam).
- Constraint: the control owner (first line) and the tester (second line) both assumed "it runs every day and the samples are clean" was the whole answer. It is half of it.
- The team conflated **design effectiveness** (would this control, if operating as described, prevent or detect the risk?) with **operating effectiveness** (did it actually operate consistently over the period?). Passing the second tells you nothing if the first fails.

## Attempts

- Tried: report "effective" on the 25/25 operating-effectiveness sample. Outcome: rejected — a control can operate flawlessly and still be the wrong control. If the reconciliation compares the wrong two populations, 25 clean samples just prove it consistently does the wrong thing.
- Tried: grounded the two-part test against the standard controls-assurance framing rather than memory. The widely-described sequence is **design effectiveness first, then operating effectiveness**: design asks "is this control designed such that, if someone followed it exactly, it would prevent or detect the error/fraud?" — typically assessed via a **walkthrough** + one-instance inspection; operating effectiveness then asks "did it operate consistently over the period?" — assessed via a sample sized to the control's frequency (e.g. ~25 for a daily control, far fewer for a quarterly one, per common AICPA-aligned sampling guidance) `[verify-at-use — sample sizes are auditor/standard-specific]`. The control type matters too: a **detective** control (this reconciliation) is judged on whether it *surfaces* the exception after the fact; a **preventive** one on whether it *stops* it before it happens (see the control-type tree in [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md)). Outcome: established that the missing step was a design-effectiveness walkthrough.
- Tried (the move that worked): ran a design walkthrough first — traced one real exception end-to-end through the reconciliation. It surfaced that the control compared the operational ledger to *itself*, not to the independent source it was supposed to reconcile against, so it was structurally incapable of catching the exception type it owned. The operating test had been clean precisely *because* the control never flagged anything. Reported a **design-effectiveness finding** (not an operating one) with an owner, a target remediation date, and a re-test gated on an independent re-tester (the `exam-remediation-has-an-owner-date-and-independent-tester` and `control-testing-design-before-operating-effectiveness` best practices). Outcome: the real gap was caught before the self-assessment falsely asserted "effective."

## Resolution

The error was testing operating effectiveness without first confirming design effectiveness — a clean sample on a mis-designed control is a false assurance, the most dangerous kind. The fix: walk the control through design effectiveness **first** (would it detect the risk if operated perfectly?), and only then test operating effectiveness; classify the finding by which one failed; and remediate with an owner, a date, and an independent re-test.

**Action for the next tester hitting this pattern:** confirm **design** before **operating** — a passed operating test on an undesigned-for-the-risk control is worse than no test, because it manufactures false comfort. Run a walkthrough, name the control type (preventive / detective / corrective) and judge it on the right question, size the operating sample to the control's frequency (`[verify-at-use]` against the applicable standard), and write every finding with an owner + date + independent re-tester (CLAUDE.md §3 #5). Keep the three lines distinct — the first line owns the control, the second tests it, the third assures the testing (CLAUDE.md §3 #3). This is controls analysis, not an audit opinion or legal advice; pair with `finance` `audit-prep-specialist` if a SOC/external-audit opinion is in scope.

**Sources (retrieved 2026-06-05):**
- A2Q2 — Controls Testing: Design Effectiveness and Operating Effectiveness (SOX 404 / AS 5): https://a2q2.com/part-8-controls-testing-design-effectiveness-and-operating-effectiveness-demystifying-sox-404-auditing-standard-5/
- Flow GRC — Preventive, Detective, and Corrective Controls: https://www.flowgrc.com/blog/preventive-detective-corrective-controls

These are practitioner framing sources for the design-vs-operating distinction and control types. Specific sampling standards, materiality, and what constitutes a reportable finding are `[verify-at-use]` against the applicable auditing/assurance standard and the firm's own testing methodology before any deliverable.
