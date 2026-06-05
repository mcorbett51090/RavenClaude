# Build a post-purchase sequence before scaling acquisition

**Status:** Absolute rule
**Domain:** DTC retention
**Applies to:** `ecommerce-dtc`

---

## Why this exists

The most common DTC growth trap is scaling paid acquisition before a post-purchase sequence exists to convert the first-time buyer into a second-time buyer. CAC rises every year; the post-purchase window (0–72 hours after first delivery) is the highest-intent moment a new customer will ever be in, and most brands leave it to a generic transactional email. A brand that converts 28% first-time buyers to second purchases with no sequence will convert ~38–45% with a well-designed one — making every CAC dollar work harder.

## How to apply

Design and instrument the post-purchase sequence before adding a new paid channel or increasing spend on an existing one.

Minimum viable post-purchase sequence (3 emails + 1 SMS):

```
T+0h:  Order confirmation (transactional — required)
T+24h: "Your order is on the way" — social proof + education on product benefit
T+3d:  Delivery confirmation + usage/first-experience guide
T+7d:  "How's it going?" + review ask + cross-sell (category-adjacent, 1 product)
T+21d: Replenishment or "it's time for more" (for consumables) OR loyalty invitation
```

**Do:**
- Gate meaningful acquisition budget increases on having a post-purchase sequence live and instrumented.
- Track second-purchase rate (30-day and 60-day windows) as the primary sequence health metric.
- Personalize at minimum by product category purchased (different sequence for skincare vs. supplements).

**Don't:**
- Launch a new channel without a sequence capable of handling the volume and product mix it will generate.
- Treat the post-purchase sequence as an email-marketing task rather than a unit-economics lever.
- Bundle the "review ask" into the order-confirmation email — wait for delivery.

## Edge cases / when the rule does NOT apply

For pure one-time purchase categories (custom engraving, one-off wedding items), the second-purchase goal shifts to referral generation — redesign the sequence end goal accordingly. Enterprise / wholesale DTC channels with account-manager relationships run a different nurture motion; this rule is for direct consumer flows.

## See also

- [`../agents/retention-analytics-analyst.md`](../agents/retention-analytics-analyst.md) — tracks second-purchase rate and sequence effectiveness.
- [`./retention-is-the-profit-engine-the-second-purchase-is-everyt.md`](./retention-is-the-profit-engine-the-second-purchase-is-everyt.md) — the master rule this operationalizes.

## Provenance

Operationalizes §3 #3 ("Retention is the profit engine — the second purchase is everything") with a concrete pre-scaling gate. The 28.2% average second-purchase figure is from the plugin's `knowledge/ecommerce-benchmarks-2026.md`; the sequence lift estimate is `[unverified — training knowledge]` — validate against the brand's own A/B data.

---

_Last reviewed: 2026-06-05 by `claude`_
