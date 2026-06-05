# Payback period is the cash constraint, not just LTV:CAC

**Status:** Pattern
**Domain:** DTC unit economics
**Applies to:** `ecommerce-dtc`

---

## Why this exists

LTV:CAC tells you whether the economics are profitable in the long run. Payback period tells you how long you're out of pocket. A brand can have a healthy 4:1 LTV:CAC and still be cash-starved because the CAC is recovered in month 18 while inventory and ad spend are billed in month 1. Capital-constrained DTC brands — which is most of them — need to know the payback window, not just the ratio. A channel that pays back in 6 months at a 3:1 ratio is safer to scale than one that pays back in 24 months at a 5:1 ratio if the brand doesn't have the balance sheet to float the gap.

## How to apply

Calculate payback period as the number of months until cumulative gross margin from a cohort equals the original CAC. Run it by channel, not blended.

```
Payback period formula (by channel cohort):
  CAC_channel ÷ (monthly_gross_margin_per_customer)
  = months until CAC is recovered

Example:
  CAC (Meta Paid): $62
  Avg monthly gross margin per retained customer: $11
  Payback: 62 ÷ 11 = 5.6 months

  CAC (Affiliate): $38
  Avg monthly gross margin: $6
  Payback: 38 ÷ 6 = 6.3 months
  — lower CAC but longer payback because lower margin/month
```

**Do:**
- Report payback period alongside LTV:CAC in every channel-efficiency analysis.
- Flag channels with payback > 12 months as capital-intensive for a bootstrapped or tightly-funded brand.
- Use payback period — not LTV:CAC alone — when deciding how aggressively to scale a channel.

**Don't:**
- Present LTV:CAC without a payback period when the client is cash-constrained.
- Use blended payback periods to make decisions about individual channels.
- Assume a "good" LTV:CAC ratio means the brand can afford to scale the channel.

## Edge cases / when the rule does NOT apply

For well-capitalized brands with a multi-year growth mandate and access to growth capital, a longer payback period is a deliberate investment, not a constraint. The rule is most binding for bootstrapped, angel-funded, or early-stage brands where cash flow is the actual operating limit. Subscription-first brands often have faster payback profiles because the first charge arrives before month 2; model accordingly.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — builds the cohort-level analysis that feeds payback calculations.
- [`./contribution-margin-not-revenue-is-the-scoreboard.md`](./contribution-margin-not-revenue-is-the-scoreboard.md) — the companion rule on which margin figure feeds the payback denominator.

## Provenance

Codifies standard DTC capital-efficiency practice; the payback-period-vs-LTV:CAC distinction is a core output of the retention analytics discipline. Motivated by the frequent error pattern where operators report healthy LTV:CAC while running the brand on a line of credit to float the ad-spend gap.

---

_Last reviewed: 2026-06-05 by `claude`_
