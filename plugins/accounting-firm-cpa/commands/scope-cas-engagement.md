---
description: "Scope, price, and design the monthly close calendar for a new CAS (Client Accounting Services) engagement — covers tier determination, tech-stack recommendation, fee model, SLA design, and client-responsibility checklist."
argument-hint: "[context, e.g. 'retail LLC, ~300 tx/month, currently on spreadsheets, no in-house controller, wants monthly financials and cash-flow forecast']"
---

You are running `/accounting-firm-cpa:scope-cas-engagement`. Use the `cas-engagement-lead`
discipline and the `client-accounting-services` skill.

## Steps

1. **Independence check.** Determine if the client also has an attest engagement at the firm.
   If yes, traverse the engagement-type / independence tree in
   `knowledge/cpa-firm-decision-trees.md` before proceeding. CAS creates a self-review threat
   for attest clients — document the analysis.

2. **Tier determination.** Based on the context provided (entity type, transaction volume,
   reporting requirements, in-house staff), assign the engagement to a service tier:
   bookkeeping-only / close-and-reporting / outsourced-controller. Justify the tier
   assignment.

3. **Tech-stack recommendation.** From the 2026 capability map in
   `knowledge/cpa-firm-decision-trees.md` (`[verify-at-use]`), recommend: general ledger,
   AP automation, expense management, and payroll platform. If a migration is required from
   current software, flag it as a separate scoping item.

4. **Monthly close calendar.** Design a day-by-day close calendar (business days from
   month-end) with task descriptions, owner (firm vs. client), and due dates. Match depth
   to the assigned tier.

5. **Deliverables list.** Enumerate every monthly deliverable (financial statements, bank
   rec summary, management report, cash-flow forecast if controller tier, etc.) with format
   and delivery date.

6. **Fee model.** Estimate monthly charge hours by task category. Apply target realization
   rate. Set the fixed monthly retainer. Define overage triggers (transaction threshold,
   additional entities, ad-hoc requests). Use `scripts/firm_calc.py` for the realization
   and fixed-fee margin checks.

7. **Client-responsibility checklist.** List what the client must do and by when: upload
   receipts, provide bank statements, approve payroll, respond to open items. These go
   into the engagement letter.

8. **Engagement letter summary.** Produce a scope summary ready to be inserted into
   `templates/engagement-letter.md`. Include: services, deliverables, SLAs, client
   responsibilities, fee, overage triggers, and term.

9. **Output.** Emit the Structured Output block with handoffs: `firm-practice-lead`
   for margin analysis; `firm-advisory-lead` for upsell opportunities above the scoped tier.
