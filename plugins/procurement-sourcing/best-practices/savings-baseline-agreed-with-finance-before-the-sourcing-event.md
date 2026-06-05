# Agree the Savings Baseline With Finance Before the Sourcing Event

**Status:** Absolute rule
**Domain:** Savings measurement / FP&A interface
**Applies to:** `procurement-sourcing`

---

## Why this exists

Procurement savings claims that finance does not recognize are a political liability and a credibility problem. The most common cause is that procurement and finance use different baselines: procurement calculates savings against last year's price; finance compares against the budget. If the budget already assumed a renegotiation, procurement's "savings" against the prior price are partially or fully already in the plan, and the CFO sees procurement claiming credit for something that was already budgeted. The fix is simple — agree the baseline with finance before the sourcing event begins — but it requires a deliberate handshake that most procurement teams skip because it slows down the timeline.

## How to apply

Before launching any sourcing event with a savings target, document the agreed baseline in writing with the relevant finance stakeholder.

```
Savings Baseline Agreement — Required Fields
──────────────────────────────────────────────────────
Category:              <name>
Spend in scope:        $X,XXX,XXX (annualized, based on volume forecast from the business)

Baseline price / rate:
  Finance-recognized baseline: $X.XX per unit / $X,XXX per month
  Source: <GL account — prior 12 months actual> or <budget rate — FY2026 AOP>
  Agreed by: <Finance name + title>  Date: <YYYY-MM-DD>
  Procurement agreed by: <Procurement name>  Date:

Volume assumption:
  Volume used in savings calculation: <X units / year>
  Source: <BU demand forecast, dated YYYY-MM-DD>

Savings recognition method:
  □ Run-rate savings (annualized impact of the new rate vs. the agreed baseline)
  □ Year 1 cash savings (actuals in the current fiscal year)
  □ NPV savings (if contract term > 3 years)
  Which method: <state>  Agreed by Finance: <name> Date:

Savings excluded from claim:
  □ Savings already in the budget / AOP
  □ Savings from volume reduction (demand management, tracked separately)
  □ Savings from specification change (not a sourcing saving)
```

**Do:**
- Get the baseline agreement in writing (email confirmation minimum) before the sourcing event launches.
- Reconfirm the baseline if the sourcing timeline slips into a new fiscal year — the relevant base period changes.
- Report savings against the agreed baseline only; do not retroactively rebase if the achieved rate turns out to be less than hoped.

**Don't:**
- Report savings against a different baseline than what was agreed without an explicit renegotiation of the methodology.
- Claim demand-management savings (reducing the amount you buy) as a sourcing saving — they are separate and should be tracked separately.
- Allow the savings report to use a volume different from what was agreed in the baseline; volume assumptions are part of the agreement.

## Edge cases / when the rule does NOT apply

- **Exploratory should-cost / market analysis** (no sourcing event yet) — baseline agreement is not required for an analysis that is not yet driving a savings claim; agree the baseline when the event is launched.
- **Spot purchases** below a defined threshold — a simplified prior-price comparison memo suffices; the full baseline agreement form is not required.

## See also

- [`../agents/spend-analytics-analyst.md`](../agents/spend-analytics-analyst.md) — owns savings measurement and the finance-reconciliation process.
- [`./realized-savings-negotiated-savings-track-to-the-pl.md`](./realized-savings-negotiated-savings-track-to-the-pl.md) — the upstream rule on tracking realized savings to the P&L; an agreed baseline is the precondition for that tracking to work.

## Provenance

Codifies the sourcing-lead and spend-analytics-analyst joint discipline from the procurement-sourcing plugin's CLAUDE.md §3 #3 (realized savings ≠ negotiated savings — track to the P&L) and the `skills/validate-realized-savings/SKILL.md`. The pre-event baseline agreement with finance reflects standard procurement governance practice in mature P&C, financial services, and manufacturing procurement functions.

---

_Last reviewed: 2026-06-05 by `claude`_
