# Project Fee Burn Must Be Tracked Weekly, Not at Billing

**Status:** Pattern
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

A project that discovers it has burned 80% of its phase fee at 60% completion — during the invoice run — is already in trouble. The billing cycle is a lagging indicator; by the time the cost-to-fee gap surfaces in an invoice, the options to respond are expensive (add staff, compress schedule, accept the loss). Weekly fee-burn tracking against phase-budget gives the PM a 2–4 week window to act: stop the overrun with a scope conversation, request an ASA, or restructure the remaining work — while there is still time to close the gap.

## How to apply

Run a weekly burn report for every active project. The minimum viable format:

```
Weekly Project Fee-Burn Snapshot
──────────────────────────────────
Project:      ________________
Phase:        ________________  Phase budget: $________
Week ending:  ________________

Hours this week (by discipline):
  Architecture:     ___   Interiors: ___   Structural coord: ___   Admin: ___
  Total hours:      ___

Fee burned this week:       $________
Fee burned to date:         $________  (___% of phase budget)
Phase completion (% est.):  ___%

Burn ratio (fee % ÷ completion %):  ___  [target: ≤ 1.0]

Status:
  [ ] On track (burn ratio ≤ 1.0)
  [ ] Caution (burn ratio 1.0–1.2; monitor)
  [ ] Over (burn ratio > 1.2; action required this week)

Action if over: _______________________________________________
```

**Do:**
- Calculate the burn ratio every week: fee-percent-burned ÷ phase-completion-percent. A ratio above 1.0 means the project is spending faster than it is progressing.
- Escalate any burn ratio above 1.2 to the project principal the same week — not at the monthly project review.
- Use the weekly report as the primary input to the monthly billing run, not the other way around.

**Don't:**
- Use only a cumulative "hours billed" report without a phase-completion denominator — it is the ratio that signals the problem, not the absolute hours number.
- Let a caution-status project go three consecutive weeks without an action; caution that doesn't resolve becomes over.
- Confuse budget-to-complete with fee remaining — if the project is over-burned, the fee remaining may not be sufficient to complete; those are different numbers.

## Edge cases / when the rule does NOT apply

Pure hourly reimbursable engagements with no fixed fee have no burn-ratio target — the billing accumulates against actual cost. The weekly report for those projects tracks hours and total-to-date cost rather than a phase budget.

## See also

- [`../agents/aec-project-analyst.md`](../agents/aec-project-analyst.md) — owns fee-burn analysis and project economics reporting.
- [`./phase-load-the-fee-to-the-effort-not-a-flat-percentage.md`](./phase-load-the-fee-to-the-effort-not-a-flat-percentage.md) — the upstream rule on phase-loaded fee budgets that make burn tracking meaningful.

## Provenance

Codifies CLAUDE.md §3 #1 (phase-load the fee to the effort) and §3 #4 (net multiplier and utilization are the firm's master numbers) at the project level. Weekly fee-burn tracking as a PM discipline is a standard practice-management recommendation in AIA and PSMJ resources on project financial management [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
