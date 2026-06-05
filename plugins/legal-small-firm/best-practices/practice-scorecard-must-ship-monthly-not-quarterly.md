# Practice Scorecard Must Ship Monthly, Not Quarterly

**Status:** Pattern
**Domain:** Small-firm legal practice
**Applies to:** `legal-small-firm`

---

## Why this exists

A quarterly scorecard is a historical document that tells you what went wrong six weeks ago. In a small firm where one slow month can materially affect annual collected revenue, the feedback loop needs to be monthly. A monthly scorecard catches a realization decline, an A/R aging trend, or a utilization gap while there is still room to adjust billing cadence, initiate collection conversations, or accept new matters — not after the quarter has closed with the miss already baked in.

## How to apply

The monthly scorecard contains five core metrics, each with a current value, a prior-month value, and a trailing-3-month average:

```
Monthly Practice Scorecard
────────────────────────────
Month:  _______________
Attorney(s):  _______________

Metric                        | This month | Prior month | T-3 avg | Target
──────────────────────────────|────────────|─────────────|─────────|────────
Collected revenue             | $          | $           | $       | $
Billed realization (%)        |            |             |         |
Collected realization (%)     |            |             |         |
Billable utilization (%)      |            |             |         |
A/R 60+ days (% of total A/R) |            |             |         |
──────────────────────────────|────────────|─────────────|─────────|────────

Open matters:     ___   New matters this month:  ___   Closed this month: ___
New intake (leads screened / accepted / declined):  ___  /  ___  /  ___

Flags:
  [ ] Realization below target
  [ ] Utilization below target
  [ ] A/R aging trend upward
  [ ] Intake volume change (needs BD response)
```

**Do:**
- Run the scorecard within the first five business days of the following month — it is a lagging indicator, but a short lag.
- Review it with a 3-month trend lens, not just point-in-time — a single bad month is noise; two consecutive months is a signal.
- Attach a one-sentence action decision to any flag: "A/R aging up → initiate payment-plan conversations on the three matters over 90 days by [date]."

**Don't:**
- Allow the scorecard to become a data-dump without targets — without a target, the numbers have no interpretive frame.
- Build the scorecard only at year-end for tax purposes — it becomes a historical curiosity, not a management tool.
- Track only collected revenue without the realization and utilization context — revenue without the efficiency metrics hides whether the practice is healthy or just temporarily busy.

## Edge cases / when the rule does NOT apply

A practice in its first three months of operation may not have enough history for a trailing-3-month average to be meaningful; use cumulative-since-launch as the baseline until three months of data exist.

## See also

- [`../agents/legal-operations-analyst.md`](../agents/legal-operations-analyst.md) — owns the scorecard build and monthly reporting.
- [`./realization-waterfall-reporting.md`](./realization-waterfall-reporting.md) — the companion rule on structuring the realization component of the scorecard.

## Provenance

Codifies CLAUDE.md §3 #1 (realization is the practice's truth) and §3 #5 (utilization is a capacity story) in a single recurring cadence. Monthly vs. quarterly reporting cadence for small-firm KPIs is a consistent recommendation in ABA and Thomson Reuters law firm practice management guidance [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
