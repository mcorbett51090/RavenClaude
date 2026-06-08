---
scenario_id: 2026-06-08-compliance-question-routed-not-rendered
contributed_at: 2026-06-08
plugin: mortgage-lending
product: compliance
product_version: "n/a"
scope: likely-general
tags: [compliance, fair-lending, routing, cost-to-originate]
confidence: medium
reviewed: false
---

## Problem

An ops analyst spotted what looked like a pricing disparity across a protected-class proxy and was tempted to declare it a fair-lending violation (or to dismiss it) in the readout. The risk: rendering a TRID/ECOA/HMDA/fair-lending determination in-team is an existential error — that judgment is counsel's, and an in-team verdict either creates false comfort or unfounded alarm (§3 #6 #8).

## Context

- Channel: retail, multiple branches.
- Constraint: the team frames operational compliance workflow and QC signals but never renders a regulatory determination — that routes to counsel (§3 #6, §2).
- The analyst was reasoning toward an in-team verdict.

## Attempts

- Tried: **separated the operational signal from the regulatory determination** (Tree 3). Outcome: the disparity was framed as a QC/operational signal to investigate, not a verdict.
- Tried: **assembled the operational facts** (pricing workflow, exceptions) without drawing a legal conclusion (§3 #6). Outcome: a clean packet for counsel.
- Tried: **routed the determination to counsel** explicitly, with the cost/process context attached (§2). Outcome: counsel — not the team — owns the fair-lending call.

## Resolution

The response was to **frame the operational signal and route the fair-lending determination to counsel** — neither declaring a violation nor dismissing it in-team. The output was the operational signal packet and an explicit routing to counsel, with no borrower NPI exposed.

**Action for the next consultant hitting this pattern:** **never render a TRID/ECOA/HMDA/fair-lending determination in-team — frame the operational signal and route it to counsel.** An in-team verdict is either false comfort or unfounded alarm; counsel owns the call. See Tree 3 and the `route-compliance` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
