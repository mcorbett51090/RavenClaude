---
description: "Design, scope, price, and operate Client Accounting Services (CAS) engagements: bookkeeping through outsourced-controller services, monthly close-as-a-service, tech-stack selection, and SLA design."
---

# Client Accounting Services (CAS)

**Purpose:** help a CPA firm scope, price, staff, and operate CAS engagements that deliver a
consistent monthly close to small-business clients — from transaction bookkeeping through
outsourced-controller services — while maintaining acceptable firm margins and clear
engagement-letter boundaries.

---

## Entry point

Spawn when asked to scope a new CAS engagement, design a monthly close process, select a
tech stack, or build a CAS pricing model. Primary agent: `cas-engagement-lead`. Supporting:
`firm-practice-lead` (economics), `firm-advisory-lead` (upsell above controller tier),
`audit-engagement-lead` (independence check if the client also has an attest engagement).

---

## CAS service tier design

Define service tiers clearly before pricing. Three standard tiers:

| Tier | Scope | Typical deliverables | Pricing approach |
|---|---|---|---|
| Bookkeeping-only | Transaction coding, bank rec, accounts payable matching | Monthly bank rec, trial balance | Fixed monthly retainer |
| Close-and-reporting | Bookkeeping + accruals + adjusting JEs + financial statements | P&L, balance sheet, cash-flow statement | Fixed monthly retainer |
| Outsourced controller | Close-and-reporting + budget-vs-actual + cash-flow forecast + advisory calls + lender support | All above + management report package + KPI summary | Fixed monthly retainer + optional project fees |

Tier assignment is based on client complexity, not client preference. An entity with 5+ bank
accounts, multiple revenue streams, or accrual-basis reporting requirements cannot be served
at the bookkeeping-only tier without material risk of error.

---

## Phase 1: Scoping a new engagement

1. **Client intake assessment:**
   - Entity type and industry
   - Transaction volume (transactions per month, by category)
   - Existing accounting software and data quality
   - Current accounting staff (in-house vs. none)
   - Reporting requirements (bank covenants, investors, management)
   - Payroll: in-house, outsourced, or to be set up
2. **Tier determination.** Match complexity to tier using the assessment above.
3. **Tech-stack fit check.** Evaluate current software against the recommended stack
   (see capability map in [`../../knowledge/cpa-firm-decision-trees.md`](../../knowledge/cpa-firm-decision-trees.md)).
   Flag migration requirement if current software is inadequate.
4. **Independence check.** If the client also has an attest engagement at the firm, route
   through `audit-engagement-lead` before finalizing scope. CAS can create a self-review
   threat if the firm also issues an audit or review report.
5. **Hours estimate.** Estimate monthly charge hours by task (transaction coding, bank rec,
   accruals, report preparation, client calls). Apply target realization rate to set the fee.
6. **Engagement letter.** Document scope, deliverables, SLAs, client responsibilities, fee,
   overage triggers, and term/termination. Use
   [`../../templates/engagement-letter.md`](../../templates/engagement-letter.md).

---

## Phase 2: Tech-stack selection and onboarding

1. **General ledger selection.** Match to client size and complexity:
   - QBO / Xero: up to ~$5M revenue, simple entity structure `[verify-at-use]`
   - Sage Intacct: multi-entity, fund accounting, mid-market `[verify-at-use]`
2. **AP automation.** Evaluate transaction volume vs. manual entry cost:
   - Bill.com / BILL: standard AP/AR automation for SMB `[verify-at-use]`
   - AvidXchange: higher volume, multi-location `[verify-at-use]`
3. **Expense management.** Match to company card / reimbursement workflow:
   - Ramp: corporate cards + expense management, real-time feed `[verify-at-use]`
   - Expensify: reimbursement-heavy, employee-submitted `[verify-at-use]`
4. **Payroll.** Recommend platform-neutral if client has a preference; otherwise:
   - Gusto: SMB, full-service payroll + benefits `[verify-at-use]`
   - ADP Run / Paychex Flex: larger SMB, more complex payroll needs `[verify-at-use]`
5. **Migration plan.** If a software change is required: define migration scope as a separate
   project (not included in the monthly retainer), estimate setup/migration hours, set a
   go-live date with a parallel-run period.
6. **Client training.** Document what the client does in the system vs. what the firm does.
   Unclear ownership = missed transactions.

---

## Phase 3: Monthly close operations

**Standard close calendar (business days from month-end):**

| Day | Task | Owner |
|---|---|---|
| Day 1 | Bank feeds reconciled; prior-month cutoff confirmed | Firm |
| Day 2 | Client uploads receipts / AP documentation | Client |
| Day 3 | AP/AR cutoff; payroll posting confirmed | Firm |
| Day 4 | Accruals and adjusting journal entries posted | Firm |
| Day 5 | Trial balance reviewed; anomalies investigated | Firm (senior/manager) |
| Day 7 | Financial statement draft prepared | Firm |
| Day 8 | Partner/manager review | Firm |
| Day 10 | Statements delivered to client; management call (controller tier) | Firm |

Adjust day targets based on client complexity and SLA in the engagement letter.

**Monthly close checklist:**
- [ ] All bank accounts reconciled to statement
- [ ] Accounts receivable aging reviewed; write-off items flagged
- [ ] Accounts payable matched to vendor statements
- [ ] Payroll posting verified against payroll register
- [ ] Fixed asset schedule updated (if any additions/disposals)
- [ ] Prepaid and accrued liability schedules rolled
- [ ] Revenue recognized per applicable method (cash vs. accrual)
- [ ] Inter-entity transactions eliminated (if multi-entity)
- [ ] Trial balance tied to prior-month comparative
- [ ] Financial statements reviewed for reasonableness vs. prior period and budget

---

## Phase 4: Overage and scope management

1. **Overage triggers** (defined in engagement letter):
   - Transaction volume exceeds threshold (e.g., >500 transactions/month)
   - Additional entities added to scope
   - Ad-hoc requests outside deliverables list (e.g., bank financing support, audit prep)
   - Software implementation or migration
2. **Out-of-scope conversation.** When an overage trigger fires, notify the client before
   performing the work. Quote the additional fee. Get approval in writing (email or addendum).
3. **Annual scope review.** Review engagement terms annually. Reprice if complexity has grown.
   Do not absorb scope creep indefinitely — it destroys margin and creates resentment.

---

## Anti-patterns

- CAS engagement accepted for an attest client without an independence analysis.
- Monthly fee set without an hours estimate and target realization rate — a guess is not a price.
- No client-responsibility cutoff dates in the engagement letter.
- Tech-stack migration bundled into the monthly retainer instead of scoped separately.
- Outsourced-controller tier delivered without defined report deliverables and a management call
  schedule — "controller" without deliverables is an expensive bookkeeper.

---

## Output

A CAS engagement scope document (deliverables, SLAs, tech stack, fee model, client
responsibilities), a monthly close calendar, and a tech-stack recommendation with migration notes.
Use [`../../templates/engagement-letter.md`](../../templates/engagement-letter.md) for the
engagement letter.
