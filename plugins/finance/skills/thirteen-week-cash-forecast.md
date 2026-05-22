---
name: thirteen-week-cash-forecast
description: Build and operate a 13-week direct-method cash forecast — receipts by source, disbursements by category, week-by-week roll, variance-to-prior-forecast cadence, covenant headroom view, and the trigger thresholds for management action. Reach for this skill when a business is cash-tight, in workout, lender-monitored, or post-fundraise discipline-building. Used by `treasury-analyst` (primary) and `fpa-analyst` for the longer-range bridge.
---

# Skill: thirteen-week-cash-forecast

**Purpose:** Build the standard short-horizon cash visibility tool — the 13-week direct cash forecast. Different mechanic than the indirect-method cash flow in a 3-statement model; this is the tactical instrument lenders and management ask for when the cash conversation matters. Used by `treasury-analyst` (primary).

## When to use

- Liquidity-tight situations (any time runway < 12 months without committed financing)
- Covenant-monitored lending relationships
- Workout / restructuring engagements
- Pre-IPO / pre-strategic-event discipline-building
- Acquisition integration (during the first 2-4 quarters)
- After any near-miss on cash (one bad month is a wake-up; two is a process gap)
- Recurring discipline for any business with material seasonality, customer concentration, or working-capital intensity

## Why 13 weeks

Long enough to see a full quarter and a regulator/lender filing window. Short enough that every line is forecastable from real receivables / payables / payroll dates — not extrapolated from a P&L.

13 weeks ≈ one quarter. Most lender covenants test quarterly; this matches. The standard horizon is rolling (a week drops off the front, a week gets added to the back, every Monday).

## Direct method vs. indirect

This forecast is **direct method** — every line is an actual cash event (a receipt or a disbursement) with a known date. Not derived from accruals.

| Direct method | Indirect method |
|---|---|
| Cash receipts (AR collections, deposits, transfers) | Net income |
| Cash disbursements (AP runs, payroll, taxes, debt service) | ± non-cash items |
| Net cash flow | ± Δ working capital |
| Beginning cash + Net = Ending cash | = Cash from operations |

The 13W is direct method. The 3-statement model uses indirect. They reconcile but aren't the same artifact.

## Structure

A 13W cash forecast has four sections, always in this order:

1. **Beginning cash** (sum of all operating bank accounts, excluding restricted)
2. **Receipts** (grouped by source)
3. **Disbursements** (grouped by category)
4. **Net change + Ending cash** (the answer)

Optionally a 5th section: **Covenant / availability roll** (for lender-monitored businesses).

### Receipts

Group receipts the way the business collects:

| Group | Examples |
|---|---|
| Customer AR collections | By customer for top concentrations; "other" for the long tail |
| Recurring contractual | Subscription billings, milestone payments, fee accruals |
| Non-operating | Refunds, settlements, asset sales, tax refunds |
| Financing | Draws on revolver, new debt, equity issuance |

For AR collections: list the top 5-10 customers individually with their expected collection dates (read from AR aging — current bucket due now, 1-30 due next week, etc.). Apply a **discount factor** for slow payers (history is honest).

### Disbursements

Group disbursements the way the business pays:

| Group | Examples |
|---|---|
| Payroll + payroll taxes | By scheduled pay date (semi-monthly / bi-weekly / weekly) |
| AP runs | By scheduled check / ACH date with category split (vendors, contractors, professional services) |
| Rent + utilities | Lease schedule + utility cadence |
| Debt service | Interest + principal per amortization schedule |
| Capex | Approved POs only, by expected payment date |
| Taxes (income, sales, property) | Filing / payment dates |
| Equity / shareholder distributions | Per board action |
| Insurance | Renewal dates |
| One-offs / extraordinary | Restructuring, severance, settlements |

For AP: list scheduled check runs by date, sized by AP aging × DPO discipline.

### Net change + ending cash

```
Beginning cash (week start)
+ Total receipts
- Total disbursements
= Ending cash (week end, = next week's beginning cash)
```

Show ending cash as a chart — line over weeks. Where the line dips below the **minimum cash policy** (typically ≥ 1 month operating expenses, or covenant minimum, whichever is higher) is the action zone.

## Driver discipline

Each line ties to a driver, not a wish:

| Line | Driver |
|---|---|
| AR collections | AR aging × historical DSO by bucket |
| Customer X collection | Contract terms × historical lateness factor for X |
| Payroll | Headcount × loaded cost × pay frequency |
| AP run | AP aging × DPO discipline |
| Debt service | Amortization schedule (fixed) |
| Capex | Approved PO list (NOT capex budget — only committed) |
| Tax | Filing calendar |

**The forecast is only as good as the AR / AP aging it draws from.** Refresh the aging snapshot when the forecast updates.

## Forecast cadence + variance loop

The 13W is a **rolling forecast with a variance loop**:

| Cadence | Action |
|---|---|
| Weekly (Monday) | Refresh actuals for the prior week. Roll forward. Re-forecast next 13 weeks. |
| Weekly | Variance commentary — Actual vs. prior-week's forecast, by line, with explanation for any > $X variance |
| Monthly | Re-baseline — refresh AR/AP aging snapshots, refresh customer-collection-rate factors |
| Quarterly | Re-examine driver assumptions (DSO, DPO trends, customer concentration changes) |

**Variance discipline.** Track variance-to-prior-forecast separately from variance-to-budget. The 13W variance commentary is about *forecast quality*, not *operating performance*. A consistently low-forecast (actuals > forecast) means the model is under-calling collections. Adjust the model, not just the explanation.

## Covenant headroom view

For lender-monitored businesses, append a covenant section:

```
Covenant: Minimum liquidity = $X (greater of $5M or 1 month opex)
Current: Ending cash + revolver availability
Headroom: Current - Covenant (must be > 0)
Trigger zones:
  - Green: > 1.5x covenant
  - Yellow: 1.0x - 1.5x covenant — proactive lender notice
  - Red: < 1.0x covenant — covenant breach (or imminent)
```

Show headroom as a line chart over the 13 weeks. Where it enters yellow is the action zone.

Same approach for revolver covenants (borrowing base, fixed charge coverage, leverage), debt service coverage, and minimum liquidity all live in the same view.

## Stress scenarios

Standard 3-scenario set for 13W:

| Scenario | Adjustments |
|---|---|
| Base | Driver-based as built |
| Downside | -20% collections, +10 days DSO, +5% disbursements, no financing inflows |
| Stress | -40% collections, no AR receipts past week 4, all discretionary capex deferred, no financing |

Show the worst-week ending cash for each scenario. If the **Downside** scenario dips below minimum cash policy within 13 weeks, that's an immediate action item.

## Trigger thresholds + management action

Pre-defined action triggers in the model:

| Threshold | Action |
|---|---|
| Ending cash forecast < 1.5x policy at any week | Notify CFO; review payable timing |
| Ending cash forecast < 1.0x policy at any week | Escalate to CEO; defer discretionary capex; tighten payable cadence |
| Covenant headroom < 1.5x at any week | Notify lender (proactive); prepare quarterly compliance certificate early |
| Covenant headroom < 1.0x at any week | Emergency: notify lender, identify waiver path or equity-cure |
| Downside scenario violates covenant within 8 weeks | Initiate refinancing / waiver conversation now |

Triggers in the model are non-negotiable. The conversation about whether to act is downstream of the trigger firing.

## Receipt-collection rate discipline

Track historical collection rates by customer / segment for at least 12 months. Forecast using the rate, not the gross.

| Customer | Expected collection (current bucket) | Historical rate | Forecast |
|---|---|---|---|
| Customer A (large enterprise) | $500K | 95% within term | $475K wk 1 |
| Customer B (mid-market) | $200K | 80% within term, 20% +30 days | $160K wk 1 + $40K wk 5 |
| Customer C (SMB) | $100K | 60% within term, 30% +30 days, 10% +60 days | $60K + $30K + $10K split across weeks |

The 13W is honest. Wishful collection assumptions are the most common failure mode.

## Lender-pack output

For lender-monitored businesses, the 13W becomes part of the regular borrower report:

- Weekly ending-cash chart (3-scenario)
- Covenant-headroom chart (3-scenario)
- Variance-to-prior-forecast table
- Material changes since last report (in commentary)
- Source-cite every line that's not internally generated

See [`./board-pack-composition.md`](./board-pack-composition.md) for lender-pack specifics.

## Common failure modes

- **Indirect method dressed up** — built off the P&L with a "+/- working capital" adjustment. Not a 13W. Build direct.
- **Collection assumptions = gross AR** — assumes every customer pays on the day they're due. Doesn't happen. Apply a rate.
- **Capex from the budget, not commitments** — only committed POs go in the 13W. Budgeted-but-not-PO'd capex belongs in a longer horizon.
- **No variance loop** — model produced once, never compared to actuals. Forecast quality never improves.
- **One scenario** — base only. The 13W's value comes from showing the downside path.
- **Stale aging** — the 13W is only as good as the AR / AP aging it pulls from. Refresh weekly.
- **Misalignment with 3-statement** — the 13W's monthly average disbursements should reconcile (loosely) to the 3-statement model's opex line. If they don't, one of them is wrong.

## Hygiene checklist

Before declaring a 13W refresh done:

- [ ] AR aging snapshot is current (within 3 business days)
- [ ] AP aging snapshot is current
- [ ] Payroll dates and amounts are correct for the next 13 weeks
- [ ] All committed capex is reflected with expected payment dates
- [ ] Debt-service amounts match amortization schedules
- [ ] Tax-filing calendar is current
- [ ] Customer-by-customer collection rates reflect last-12-month history
- [ ] All scenarios populated (Base, Downside, Stress)
- [ ] Covenant calculation rolled through every week
- [ ] Variance-to-prior-forecast filled in for the actuals week
- [ ] Triggers checked; action items raised where they fired
- [ ] Reviewer signed off

## See also

- Skill: [`./month-end-close.md`](./month-end-close.md) — the close cadence the 13W shouldn't conflict with
- Skill: [`./board-pack-composition.md`](./board-pack-composition.md) — lender-pack specifics (covenant-compliance, borrowing-base)
- Template: [`../templates/cash-flow-forecast.md`](../templates/cash-flow-forecast.md)
- Agent: [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md)
- Agent: [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md)
