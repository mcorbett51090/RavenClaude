# Email and SMS are retention channels, not acquisition substitutes

**Status:** Pattern
**Domain:** DTC retention and channel strategy
**Applies to:** `ecommerce-dtc`

---

## Why this exists

When paid acquisition costs climb, DTC brands are often tempted to "work the email list harder" to compensate — increasing send cadence, promoting to cold leads, treating the list as a cheap replacement for paid media. This inverts the purpose of the channel. Email and SMS are owned retention channels that compound when used for post-purchase nurture, repeat-purchase triggers, and loyalty; they decay when used as a blasting tool for acquisition-style conversion. A list that's burned with promotional overload has a shrinking effective reach and a rising unsubscribe rate that reduces its long-term value.

## How to apply

Segment the email and SMS list by lifecycle stage and message accordingly. Post-purchase flows, replenishment reminders, and VIP loyalty communications should consume the majority of email and SMS send volume. Promotional blasts go to warm segments only.

```
List segmentation model:
  Segment 1 — New (0–30 days post-purchase): onboarding flow, education, first-repeat trigger
  Segment 2 — Active (1–3 purchases, last 90 days): loyalty progression, cross-sell
  Segment 3 — Lapsing (90–180 days no purchase): win-back sequence (max 3 touches)
  Segment 4 — Churned (180+ days): suppress from promo sends; quarterly reactivation only
  Segment 5 — VIP (top 10% LTV): early access, community, higher-cadence acceptable

Promo blast = Segments 1+2+active VIP only. Never Segments 3+4 by default.
```

**Do:**
- Build triggered lifecycle flows first (post-purchase, replenishment, win-back) before building a promotional calendar.
- Suppress lapsing and churned segments from broad promotional sends.
- Track email/SMS attribution separately from paid channels in the contribution margin model.

**Don't:**
- Increase email/SMS send frequency as a direct response to rising CAC on paid channels.
- Send acquisition-framed copy ("Meet [Brand]!") to existing customers.
- Use a single unsegmented list for all campaign types.

## Edge cases / when the rule does NOT apply

Launch campaigns for a new product line reasonably go to the full active list — the novelty justifies broader reach. Major promotional events (Black Friday, brand anniversary) may warrant broader segmentation temporarily. For brands with fewer than 5,000 list subscribers, the segmentation overhead may exceed the benefit; apply the lifecycle-flow principle without formal segments.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — tracks the repeat-purchase metrics that measure email/SMS effectiveness.
- [`./retention-is-the-profit-engine-the-second-purchase-is-everyt.md`](./retention-is-the-profit-engine-the-second-purchase-is-everyt.md) — the anchor rule on why owned-channel retention compounds.

## Provenance

Codifies the team's standing bias against using owned channels as acquisition-channel substitutes, grounded in lifecycle-marketing principles. The send-cadence-as-CAC-hedge pattern is one of the most common anti-patterns observed when acquisition costs rise; this rule documents the correct framing.

---

_Last reviewed: 2026-06-05 by `claude`_
