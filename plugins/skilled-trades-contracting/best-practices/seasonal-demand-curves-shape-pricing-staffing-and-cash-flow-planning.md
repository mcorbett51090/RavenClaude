# Seasonal Demand Curves Shape Pricing, Staffing, and Cash-Flow Planning

**Status:** Pattern
**Domain:** Business planning / operations
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

HVAC, plumbing, and electrical contractors all have seasonal demand patterns — HVAC peaks in summer and shoulder seasons, plumbing peaks in winter (freeze-thaws, holiday overuse), electrical is more even but new-construction peaks with the housing cycle. Contractors who do not model their demand curve manage their business in constant reaction: over-staffed in slow months, under-staffed in peak (turning away calls), short on cash in spring before the summer season hits. Seasonality is not a surprise — it is predictable from 3 years of historical call data, and it should drive the annual staffing, pricing, and cash-flow plan before the season arrives.

## How to apply

Build the seasonal demand model annually from historical call data:

```
Seasonal demand model (trailing 3 years, same trade):
  By month — pull from dispatch system:
    Month:         Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec
    Total calls:   ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___
    Revenue ($):   ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___
    Technician hrs:___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___  ___

  Pattern classification:
    Peak months (top 3):      ______
    Trough months (bottom 3): ______
    Peak-to-trough ratio:     ______x (if >2x, seasonal management is critical)

  Planning outputs (before each season):
    Staffing: hire/onboard before peak, not during it
      Hiring timeline: ______ weeks before peak start
    Cash flow: trough months may require a line of credit or cash reserve
      Minimum cash reserve for trough:  $______
    Pricing: consider peak pricing (higher demand = less price sensitivity)
      Peak markup vs. standard flat rate: +______%
    Maintenance agreements: sell at trough to build demand cushion for next trough
```

**Do:**
- Pull the demand curve from actual dispatch data, not intuition — the exact peak and trough months vary by market and by trade.
- Hire and train new technicians to be solo-callable at least 4–6 weeks before your historical peak start — peak is not the time for a new hire's learning curve.
- Price non-emergency work during peak at a modest premium; customers who call during peak are less price-sensitive and you have less excess capacity.

**Don't:**
- Staff to peak year-round; the fixed labor cost during the trough erases the peak margin.
- Run the business cash-flow-negative through the trough without a line of credit or reserve; the peak revenue arrives, but payroll doesn't wait for it.

## Edge cases / when the rule does NOT apply

Commercial and new-construction contractors with multi-month project backlogs have a different demand-smoothing mechanism than service-only contractors; the demand curve matters for project backlog management but less for individual call volume. Contractors in Sun Belt markets may have a flatter seasonal curve for cooling; build the model from your specific data, not a regional assumption.

## See also

- [`../agents/trades-engagement-lead.md`](../agents/trades-engagement-lead.md) — frames the seasonal demand curve as part of the business review.
- [`../agents/trade-business-analyst.md`](../agents/trade-business-analyst.md) — owns the demand model, cash-flow forecast, and staffing plan.
- [`./maintenance-agreements-are-a-recurring-revenue-engine-not-just-a-service-feature.md`](./maintenance-agreements-are-a-recurring-revenue-engine-not-just-a-service-feature.md) — maintenance agreements are the primary tool for smoothing seasonal demand; the two rules are directly linked.

## Provenance

Seasonal demand management for trade contractors is a standard topic in HVAC and plumbing contractor business coaching (Nexstar Network, Service Nation); cash-flow seasonality is documented in ACCA and CFMA contractor financial management guides.

---

_Last reviewed: 2026-06-05 by `claude`_
