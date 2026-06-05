# Track net revenue per order, not gross revenue

**Status:** Absolute rule
**Domain:** DTC unit economics
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Gross revenue is what a customer pays before any deductions. Net revenue per order (gross minus returns, refunds, chargebacks, and promotional discounts) is what actually hits the P&L before COGS. DTC brands that plan and report on gross revenue systematically overstate what the business earns — and when a return-heavy SKU category or a deep-discount promo quarter arrives, the gap between "revenue" and real cash is the delta that blows the forecast. The contribution margin calculation starts from net revenue; feeding it gross revenue produces a dangerously optimistic number.

## How to apply

Define and use net revenue per order (NRPO) as the revenue input to every unit-economics calculation.

```
Net Revenue Per Order (NRPO) formula:

NRPO = Gross Order Value
     − Discounts / Promo Codes applied
     − Returns (refunded amount, inclusive of any restocking credit)
     − Refunds (partial or full, non-return)
     − Chargebacks (gross chargeback amount)

Then: Contribution Margin = NRPO − COGS − Shipping − CAC allocation
```

Report gross revenue for top-line visibility, but run all unit-economics, LTV, and channel-efficiency calculations on NRPO.

**Do:**
- Build NRPO as a first-class field in the analytics data model — do not compute it ad-hoc at report time.
- Track the gross-to-net "leakage rate" by category (returns are a margin line, §3 #6).
- Flag any category where leakage rate exceeds 20% for immediate review.

**Don't:**
- Compute LTV from gross revenue without deducting returns and promos.
- Present revenue-per-order to the board without disclosing the leakage rate.
- Treat a promotional discount as a "marketing cost" separate from revenue — it reduces NRPO directly.

## Edge cases / when the rule does NOT apply

For subscription-only models with no returns or refunds (pure digital, SaaS-adjacent DTC), gross and net revenue converge — apply the rule anyway to track chargeback rate as its own leakage signal. Marketplace-only sellers where returns are handled by the marketplace still need to model the net payout per sale against their stated gross.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — builds the scorecard that starts from NRPO.
- [`./contribution-margin-not-revenue-is-the-scoreboard.md`](./contribution-margin-not-revenue-is-the-scoreboard.md) — the master rule; NRPO is its input.
- [`./returns-are-a-margin-line-not-a-customer-service-line.md`](./returns-are-a-margin-line-not-a-customer-service-line.md) — returns are the largest leakage driver for most categories.

## Provenance

Operationalizes §3 #2 ("Contribution margin, not revenue, is the scoreboard") by naming the revenue input that makes the margin calculation honest. Standard DTC/e-commerce financial practice; codified here because the gross-vs-net confusion is the most frequent P&L error in operator-submitted models.

---

_Last reviewed: 2026-06-05 by `claude`_
