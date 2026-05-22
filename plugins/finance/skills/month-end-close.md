---
name: month-end-close
description: Run a clean month-end / quarter-end close — close-calendar mechanics, JE buckets, reconciliation checklist, exception-triage playbook. Reconciliation before commentary; materiality as a design constraint. Used by `controller` (primary).
---

# Skill: month-end-close

**Purpose:** Reference playbook for designing and running a clean month-end close. Used by `controller` (primary), occasionally by `audit-prep-specialist` and `fpa-analyst` when their work depends on a closed period.

## When to use

- Designing a close calendar for a new entity or a refresh of an existing one
- Triaging a close that's slipping (where's the bottleneck, what's blocking)
- Reviewing JEs and accruals during close week
- Writing the post-close summary memo for management

## The standard close calendar

Days are relative to month-end (Day 0). Adjust to your entity's actual close target.

| Day | Workstream | Owner |
|---|---|---|
| Day -3 to Day -1 | Cutoff communication: sales cutoff, expense cutoff, payroll cutoff confirmed | Controller |
| Day 0 (month-end) | Sub-ledgers run their period-end posting; physical inventory if applicable | Operations + Controller |
| Day 1 | Sub-ledger posting tied to GL; bank statements pulled; AR / AP aging snapshots taken | Staff accountants |
| Day 2 | Accruals booked: payroll (residual days), vendor invoices not received, customer revenue cutoff adjustments | Staff accountants |
| Day 3 | Account recons: cash, AR, AP, accruals, prepaids, fixed assets | Staff + Senior accountants |
| Day 4 | Intercompany matching + eliminations; foreign-currency translation; CTA bucket update | Senior accountants |
| Day 5 | Top-side review: GL trial balance reviewed by controller; outlier JEs investigated | Controller |
| Day 6 | Executive review: prelim P&L / BS reviewed with CFO; adjustments identified | Controller + CFO |
| Day 7 | Final JEs posted (true-ups, reclasses); books "locked" | Controller |
| Day 7-10 | Variance commentary; KPI pack assembled; board / investor reporting | FP&A |

A 7-day close is typical for a mid-market entity with a competent team. Faster closes (3-5 days) require investment in automation; slower (10-15) usually indicates a fixable bottleneck.

## JE buckets (what's normally booked during close)

1. **Standard recurring**: depreciation, amortization, lease accretion, intangible amortization
2. **Cutoff accruals**: expenses incurred but not yet invoiced (services, utilities, bonuses)
3. **Revenue cutoff**: deferred revenue release, unbilled revenue accruals
4. **Reclasses**: misclassified entries from earlier in the period (always with a memo)
5. **Estimates and true-ups**: prior-period estimates that need refinement (utilities estimates, audit-fee accruals)
6. **Foreign currency**: revaluation of FX-denominated balances, CTA bucket
7. **Intercompany**: matching entries + eliminations on consolidation
8. **Capitalization decisions**: items moved from expense to fixed asset (or vice versa) with memo

## Reconciliation checklist

For every recon, the workpaper should show:

- [ ] Account name + GL number
- [ ] Period
- [ ] GL balance
- [ ] Source / sub-ledger balance
- [ ] Reconciling items (each with explanation + age)
- [ ] Variance (GL − Source, if any)
- [ ] Preparer signature + date
- [ ] Reviewer signature + date
- [ ] Source-doc references (file paths, ticket numbers, system exports)

**Material reconciling items > 30 days old are escalated**, not rolled forward.

## Exception triage

When close slips, run this triage:

1. **Where exactly is it stuck?** Look at the close calendar — which day's workstream didn't complete?
2. **Who owns the stuck workstream?** If the owner is overloaded across multiple workstreams, that's a resource issue, not a process issue.
3. **Is it a data problem or a decision problem?**
   - Data: source system feed is broken / late / missing — fix the feed.
   - Decision: management can't agree on an accounting treatment — escalate to CFO before close, not after.
4. **Is the bottleneck recurring?** If the same workstream slips every close, that's the next quarter's automation target.

## Documenting the close

After close, the controller publishes a short post-close memo to the management team:

- Did we close on target? If not, by how many days, and why?
- Material adjustments booked late in close (with rationale)
- Items deferred to next period (with target resolution date)
- Lessons / next-quarter improvements

This memo also feeds the audit walkthrough — auditors love a documented close process.

## Anti-patterns

- A "close" that never actually finishes — books re-opened ad hoc for weeks afterward
- Close calendar that lives only in the controller's head
- "Plug" entries to make the books tie without a memo
- Sub-ledgers reconciling to themselves rather than to the GL
- Accruals that grow indefinitely without true-up
- Material items deferred to the next period with no documented owner / target date
- Top-side review skipped because "the numbers look fine"

## See also

- Template: [`../templates/month-end-close-calendar.md`](../templates/month-end-close-calendar.md)
- Template: [`../templates/account-reconciliation.md`](../templates/account-reconciliation.md)
- Agent: [`../agents/controller.md`](../agents/controller.md)
- Skill: [`./variance-commentary.md`](./variance-commentary.md) — for the post-close FP&A handoff
