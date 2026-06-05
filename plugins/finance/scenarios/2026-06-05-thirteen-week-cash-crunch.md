---
scenario_id: 2026-06-05-thirteen-week-cash-crunch
contributed_at: 2026-06-05
plugin: finance
product: treasury
product_version: "n/a"
scope: likely-general
tags: [treasury, 13-week-cash, runway, covenant, working-capital]
confidence: medium
---

## Problem

A founder-led company saw its month-end cash balance dropping and the board asked "how many months of runway do we have?" The only artifact was an indirect-method annual cash plan rolled off net income — it showed a comfortable year-end balance and completely hid a six-week trough where a quarterly tax payment, payroll, and a large supplier settlement would land in the same fortnight. The annual view said "fine"; the weeks said "you breach the minimum-cash covenant in week 6."

## Context

- Segment: growth-stage company, one operating currency, a committed revolver with a minimum-liquidity covenant.
- Constraint: the indirect-method annual model nets timing out — it cannot show a *week* where cash dips below a buffer. The covenant was tested on a near-continuous minimum-cash basis, so a single trough week was a real breach, not a rounding issue.
- The reflex was to draw the revolver immediately to feel safe — before checking whether the shortfall was a timing gap or a structural burn.

## Attempts

- Tried: rebuilt the forecast as a **direct-method 13-week** model — actual receipts by source and disbursements by category, week by week — instead of net income roll-off. Outcome: made the week-6 trough visible and sized it; the annual view had been mathematically hiding it.
- Tried: classified the shortfall on the triage ladder — **timing gap vs. structural burn.** Outcome: it was a *timing* gap (a clustered fortnight of outflows), not burn exceeding inflow ongoing — so it was a treasury-lever problem, not an FP&A re-plan.
- Tried: walked the cash-shortfall response ladder cheapest-and-most-reversible-first — accelerate receivables / stretch payables *within terms* / defer discretionary spend — **before** any revolver draw. Outcome: pulling a deposit forward and shifting one discretionary spend covered most of the trough; a partial, covenant-safe revolver draw covered the remainder, checked against the leverage covenant *before* drawing (a draw can itself move a ratio).

## Resolution

The runway question was answered honestly at the week granularity (the annual number was not wrong, just blind to timing), the covenant breach was avoided by working-capital levers plus a small, deliberately-sized revolver draw rather than a reflexive full draw, and the model became a rolling weekly review with a variance-to-prior-forecast loop. Because the gap was diagnosed as *timing* not *structural*, no panic raise or burn-cut was triggered.

**Action for the next analyst hitting this pattern:** **forecast cash on the direct method at weekly granularity — an indirect annual roll-off hides the trough that breaches the covenant.** Classify timing-vs-structural first: a timing gap is a treasury-lever problem (working capital → committed facility → monetize → raise, in that order, cheapest and most reversible first); a structural burn escalates to FP&A to cut burn / re-plan. Test every lever against the *actual* covenant before pulling it. Canonical references: [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md) (cash-shortfall ladder + financing tree) and the [`thirteen-week-cash-forecast`](../skills/thirteen-week-cash-forecast/SKILL.md) skill. The [`../scripts/finance_calc.py`](../scripts/finance_calc.py) `runway` mode finds the trough week and the cash-out month.

**Sources (retrieved 2026-06-05):**
- Graphite Financial — why you need a 13-week cash flow forecast (direct method, weekly visibility): https://graphitefinancial.com/blog/why-you-need-13-week-cash-flow-forecast/
- BPR Global — the CFO's 13-week cash flow forecasting guide (rolling, variance loop): https://bprglobal.co/resources/financial-planning-analysis/13-week-cash-flow-forecasting-guide/

Runway rules of thumb (raise at 6–9 months remaining; warning signs under ~3 months) are common trade-literature ranges, not hard rules — `[verify-at-use]` and calibrate to the entity's risk tolerance and the actual covenant definitions (§3 #1, §3 #5).
