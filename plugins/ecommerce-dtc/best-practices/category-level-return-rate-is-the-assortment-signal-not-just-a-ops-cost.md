# Category-level return rate is the assortment signal, not just an ops cost

**Status:** Pattern
**Domain:** DTC merchandising and contribution margin
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Most DTC brands track returns as an operations and logistics cost — who handles the shipment, what's the restocking fee, what's the write-off. This framing misses the merchandising signal. A high return rate in a specific category or SKU is the most direct signal that the product is misrepresented, mis-sized, mis-priced, or wrong for the customer arriving via a specific channel. An apparel brand with a 35% return rate on one colorway SKU has a product-fit or photography problem; a supplement brand with a 22% return rate from a specific ad creative has an expectation-gap problem. The fix is upstream — in the product, the photography, or the creative — not in the reverse logistics process.

## How to apply

Instrument return rate at the SKU level and cross-reference against the acquisition channel and the return reason code. Surface the top-5 highest-return-rate SKUs in every contribution margin review.

```
Return analysis model:
  Metric: return_rate_by_sku = returns_initiated / units_sold (same 30-day cohort)

  Diagnostic cross-tabs:
    return_rate_sku × acquisition_channel → expectation-gap signal (creative or page)
    return_rate_sku × variant (size/color/flavor) → product-fit or photography gap
    return_rate_sku × return_reason_code → product quality vs. expectation vs. wrong-size

  Contribution margin adjustment:
    Net_margin_SKU = gross_margin_SKU × (1 - return_rate) - (return_rate × avg_return_cost)

  Flag threshold: any SKU with return rate > 2× category average → mandatory investigation
```

**Do:**
- Report SKU-level return rate alongside gross margin in every assortment review.
- Cross-reference return rate with the acquisition source to identify expectation-gap vs. product-quality causes.
- Use return rate as an input to range rationalization — a SKU with high return rate + low net margin is a contraction candidate.

**Don't:**
- Report returns only at the aggregate/category level — this hides the specific SKU signal.
- Treat return cost as fixed overhead without tying it to the SKU that generated it.
- Rationalize a high-return-rate SKU as "customers' preference" without checking whether the product page accurately represents the product.

## Edge cases / when the rule does NOT apply

Gift-category SKUs (especially during holiday season) have structurally higher return rates due to recipient preferences, not product quality; apply a seasonal-gift adjustment when evaluating return rate for this segment. Brands with "open-box return" policies that don't track reason codes need to invest in return survey instrumentation before SKU-level diagnosis is possible.

## See also

- [`../agents/merchandising-specialist.md`](../agents/merchandising-specialist.md) — owns assortment and product-page decisions where return rate signals a fix.
- [`./returns-are-a-margin-line-not-a-customer-service-line.md`](./returns-are-a-margin-line-not-a-customer-service-line.md) — the parent rule on treating returns as a margin problem.

## Provenance

Codifies the team's §3 #6 house opinion ("returns are a margin line, not a customer-service line") applied to the assortment level. The ops-only framing of return rate is the dominant error; the SKU-level cross-tab is where the actionable signal lives.

---

_Last reviewed: 2026-06-05 by `claude`_
