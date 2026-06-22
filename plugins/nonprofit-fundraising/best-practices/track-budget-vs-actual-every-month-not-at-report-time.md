# Track Budget-vs-Actual Every Month, Not at Report Time

**Status:** Pattern
**Domain:** Nonprofit grants — post-award compliance
**Applies to:** `nonprofit-fundraising`

---

## Why this exists

The grantee who reconciles grant spending only when a report is due is managing blind for months at a time. Two failure modes follow, and both are usually unrecoverable by the time the report surfaces them. First, the **spend-down problem**: a line that's been under-spending all year shows up as a large unspent balance in month 11, too late to either spend it well or request a no-cost extension on time. Second, the **over-spend problem**: a line quietly running over budget becomes a disallowed-cost or repayment risk that a monthly check would have caught while it was still a $400 variance instead of a $40,000 one. Monthly budget-vs-actual converts grant management from a year-end scramble into a steering wheel — you see the burn rate, you correct early, and the financial report becomes a five-minute export of numbers you already trust.

## How to apply

Reconcile actuals to the approved budget **by category, every month**:

| Track per category | Why |
|---|---|
| Approved budget | the baseline |
| Period actual + YTD actual | what's been spent |
| Remaining balance | what's left |
| % expended | pace vs. the calendar |
| Burn rate / on-pace flag | will it spend out by the period-of-performance end? |
| Variance note (>~10%) | the early-warning signal |

A line trending past a ~10% variance is the trigger to either correct the spending or request a budget modification — *before* the report shows it (many funders require a narrative for variances over a threshold, and some require prior approval). `[verify-at-use 2026-06-22 — variance/prior-approval thresholds are set by the award]`

**Do:**
- Reconcile monthly to the general ledger, by budget category — use the [`../templates/grant-budget-vs-actual-tracker.md`](../templates/grant-budget-vs-actual-tracker.md).
- Watch burn rate against the period of performance, not just the dollar balance.
- Act on a trending variance early — correct spending or request a modification with lead time.

**Don't:**
- Reconstruct a year of spending the week a report is due.
- Treat an unspent balance in the final months as recoverable — it usually isn't.
- Tie a drawdown to the budget plan; tie it to recorded, allowable expenditures.

## Edge cases / when the rule does NOT apply

A very small, single-line, short-duration grant may not warrant a monthly cadence — but even then, reconcile at least quarterly. The rule scales with award size and complexity, never to "at report time only."

## See also

- [`../knowledge/grant-management-post-award.md`](../knowledge/grant-management-post-award.md) — budget-vs-actual, drawdown, and modification detail.
- [`../templates/grant-budget-vs-actual-tracker.md`](../templates/grant-budget-vs-actual-tracker.md) — the fill-in tracker + report calendar.
- [`./spend-only-on-allowable-allocable-reasonable-costs.md`](./spend-only-on-allowable-allocable-reasonable-costs.md) — what may be charged in the first place.

## Provenance

Codifies standard grants-management financial discipline (monthly reconciliation against the approved budget). Advisory only — not accounting advice; thresholds are `[verify-at-use 2026-06-22]` pending the award terms.

---

_Last reviewed: 2026-06-22 by `claude`_
