---
name: ro-lifecycle-and-comeback-control
description: "Run the repair order from open to closed and stop comebacks at the root cause: WIP/RO aging triage (waiting on approval vs parts vs tech), parts staging before dispatch, and comeback grouping by cause (misdiagnosis, workmanship, part quality, incomplete, no-fault). Rework labor is billed at zero. No PII."
---

# RO Lifecycle & Comeback Control

The repair order is the shop's unit of work and its unit of money. Two things kill margin in its lifecycle: an RO that **sits** (aged WIP no one is moving) and an RO that **comes back** (rework billed at zero that also cost you the customer).

> **Advisory, operations decision-support.** Labor times and benchmark ranges are `[verify-at-use]`. No customer PII — reason in RO status and job flow.

## The RO lifecycle

`open → written up → authorized → dispatched → parts staged → in repair → QC → closed → follow-up`

Every stall maps to an owner. Read WIP by **age and cause**:

| RO is aging because… | Owner | Action |
|---|---|---|
| Waiting on approval | service advisor | Re-contact customer; supplemental authorization |
| Waiting on parts | parts/staging | ETA, sublet, or stage-then-dispatch |
| Waiting on a tech | dispatch | Re-dispatch to skill/availability |
| Done, not invoiced | advisor/cashier | Close and bill (unbilled = financing the customer) |

**The rule:** set a WIP-age threshold that forces action, and triage by cause — not one RO at a time.

## Comeback control (root cause, not blame)

Group every comeback by cause and fix the process that produced it:

| Cause | Root fix |
|---|---|
| Misdiagnosis | Diagnostic process, tooling, information access |
| Workmanship | Skill match / dispatch, QC step, training |
| Part quality | Supplier/matrix tier decision |
| Incomplete repair | Multi-point verification before closeout |
| No-fault (unrelated/expectation) | Write-up clarity, customer communication |

Rework is billed at zero, paid to the tech, and consumes a bay — it erodes the effective labor rate and car count at once. **Stage parts before the job starts** so a parts-hold never becomes a cold-vehicle re-diagnosis.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Comeback rate | comeback ROs / total ROs | The quiet tax on labor GP `[verify-at-use]` |
| Average RO age (open WIP) | days open, by cause | Aged WIP is stalled cash |
| Parts-hold RO count | ROs blocked on parts | Staging-discipline signal |
| First-time-fix rate | closed-without-return / total | The inverse quality read |

## Anti-patterns

- Re-fixing a comeback without finding why it came back (it returns again).
- Letting the tech who caused a comeback bill the rework as new work.
- Starting a job before parts are staged.
- Reading total WIP without splitting it by stall cause.

## See also

- Traverse the **comeback root-cause triage** tree in [`../../knowledge/auto-repair-shop-decision-trees.md`](../../knowledge/auto-repair-shop-decision-trees.md).
- [`../technician-productivity-and-efficiency/SKILL.md`](../technician-productivity-and-efficiency/SKILL.md), [`../estimate-and-dvi-workflow/SKILL.md`](../estimate-and-dvi-workflow/SKILL.md), [`../../templates/repair-order-workflow.md`](../../templates/repair-order-workflow.md).
- Best practices: [`../../best-practices/a-comeback-costs-you-twice.md`](../../best-practices/a-comeback-costs-you-twice.md).
