---
scenario_id: 2026-06-08-under-budget-until-the-ctc-landed
contributed_at: 2026-06-08
plugin: construction-field-management
product: generic
product_version: "unknown"
scope: likely-general
tags: [cost-report, cost-to-complete, budget-vs-actual, commitments, change-order]
confidence: high
reviewed: false
---

## Problem

The monthly cost report showed the job a comfortable 4% under budget at roughly 60% complete, and the owner's loan draws were being approved on that picture. The number was built as actuals-billed against the original budget. It ignored two things: a stack of approved change orders that had widened the scope but were never posted to the budget, and several signed subcontracts and material POs that were committed but not yet billed. When the PM finally built a real cost-to-complete by cost code, the "under budget" job was actually projecting a 6% overrun — and most of the bad codes were the ones still to be built, where there was the least room to recover.

## Constraints context

- Self-perform plus a dozen subs; cost codes existed but the report only tracked actual invoices posted, not commitments.
- Approved COs were tracked in the change log but never flowed into the budget column of the cost report.
- The owner was making lending decisions on the monthly number, so the gap was not just internal — it was a credibility and draw-accuracy problem.

## Attempts

- Tried: reconciling actuals more carefully and chasing late invoices. Helped the actual column but did nothing about the missing commitments or the unposted changes — still an under-budget mirage.
- Tried: adding the approved COs to the budget. Closer, but the report still read better than reality because committed-but-unbilled subcontracts and POs were invisible.
- Tried: rebuilding the report as committed vs. actual vs. forecast by cost code, with a cost-to-complete forecasting the remaining cost on every code and a projected-final-cost roll-up. This worked — the overrun surfaced with months of runway instead of at the final reconciliation.

## Resolution

Posting the approved changes to the budget, counting signed subcontracts and POs as committed cost even when unbilled, and forecasting a cost-to-complete per code turned the report honest. The projected final cost showed the 6% overrun while there was still time to act — value-engineer the unbought scope, tighten the codes that were drifting, and warn the owner before the draw was wrong rather than after. The drivers were named (two trades trending over on labor productivity), and the time-impact on the affected activities was routed to `project-management`.

## Lesson

The cost report is only honest with a cost-to-complete. Actuals-against-budget with unposted changes and unbilled commitments is a mirage that reads under-budget the month before the overrun lands. Post the changes, count the commitments, forecast a CTC by cost code, and report committed/actual/forecast/projected-final — then the overrun shows up with runway to fix it.
