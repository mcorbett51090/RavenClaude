# The win-back window closes at 180 days — act before it

**Status:** Pattern
**Domain:** DTC retention
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Most DTC brands treat a lapsed customer and a churned customer as the same: someone on the list who hasn't bought recently. They aren't. Customers who lapsed at 90–120 days still have measurable reactivation rates (often 15–25% with the right trigger); customers who passed 180 days without a second purchase have churn rates that make reactivation uneconomic against the CAC of acquiring a new customer. Acting at 90 days with a win-back sequence is cheap and effective; acting at 200 days is expensive and rarely pays back. The window closes — and most brands find out when they run the cohort analysis for the first time.

## How to apply

Define and instrument three lapse-status tiers based on days since last purchase. Build distinct communication sequences for each tier. Do not send identical promotional emails to all three.

```
Lapse-status tiers (adjust thresholds by category purchase frequency):
  At-risk (61–90 days):
    — 1–2 touches: personalized "we noticed you haven't ordered" + product recommendation
    — Target reactivation rate: 20–30% [ESTIMATE]

  Lapsing (91–150 days):
    — 3-touch win-back sequence with escalating offer (free shipping → 10% → 15%)
    — Target reactivation rate: 10–20% [ESTIMATE]

  Churned (151–180 days):
    — Last-ditch 1-2 touch "still here?" with strongest offer
    — Target reactivation rate: 5–10% [ESTIMATE]
    — After 180 days: suppress from promotional sends; quarterly check-in only

Note: replenishment-category brands (supplements, beauty) may see natural 30-day purchase windows; adjust tier boundaries to 2x the expected purchase frequency.
```

**Do:**
- Fire the at-risk trigger automatically on day 61 post-purchase (or day after expected replenishment).
- Escalate the offer incrementally across the three-touch win-back — don't lead with the max discount.
- Suppress the churned segment from broad promotional sends after 180 days to protect deliverability.

**Don't:**
- Wait for a manual review process to identify lapsed customers — automate the tier triggers.
- Send the same email to a 70-day lapse and a 160-day lapse.
- Ignore deliverability health when reactivating old segments (warm up slowly, test engagement).

## Edge cases / when the rule does NOT apply

High-consideration, low-frequency categories (furniture, mattresses) have natural purchase cycles of 3–7 years; the lapse-window thresholds must be set to multiples of the category repurchase cycle, not 90/150/180 days. Seasonal DTC brands (holiday-specific) should expect long inter-purchase gaps and define lapse relative to the seasonal cycle, not the calendar year.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — builds the cohort analysis that identifies lapse-window boundaries.
- [`./build-a-post-purchase-sequence-before-scaling-acquisition.md`](./build-a-post-purchase-sequence-before-scaling-acquisition.md) — the companion rule on building the post-purchase foundation first.

## Provenance

Codifies the team's retention discipline applied to the win-back timing problem. The 180-day threshold is a common industry heuristic for "effectively churned" in mid-frequency DTC categories; it aligns with the team's §3 #3 house opinion on the compounding importance of the second purchase.

---

_Last reviewed: 2026-06-05 by `claude`_
