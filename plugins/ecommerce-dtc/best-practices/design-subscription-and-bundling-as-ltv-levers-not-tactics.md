# Design subscription and bundling as LTV levers, not tactics

**Status:** Pattern
**Domain:** DTC product and growth
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Subscription and bundling are routinely treated as promotional tactics — a discount to juice one-time AOV or an upsell at checkout. When designed that way, they produce short-term revenue bumps and long-term churn, because the customer signed up for the deal, not the product habit. When designed as LTV levers — meaning the subscription or bundle is built around a genuine replenishment cadence, a use-case fit, or a "complete solution" logic — they shift purchase frequency and AOV permanently, compounding LTV without raising CAC. The difference between a 12-month subscriber LTV and a 3-month cancel-after-discount LTV is the entire margin story.

## How to apply

Before launching a subscription or bundle, run the LTV lever test:

```
LTV Lever Test (run before launch):

1. Is the replenishment cadence product-driven or discount-driven?
   - Product-driven: the customer runs out in 30/60/90 days → subscription fits naturally
   - Discount-driven: the customer stays subscribed only while the discount holds → churn on renewal

2. Does the bundle solve a complete use-case, or does it just group things?
   - Complete use-case: starter kit, refill kit, "the regimen" → AOV + repeat intent
   - Grouped SKUs: "we had extra inventory" → returns and regret

3. What is the expected cancel rate at renewal cycle 1?
   - Model the subscriber cohort LTV at the first cancel-eligible moment
   - A cohort with >40% first-renewal cancel rate is a discount program, not an LTV lever
```

**Do:**
- Measure subscriber cohort LTV at M3, M6, and M12 — not just initial conversion rate.
- Design bundle SKU selection around problem-solution fit (e.g., cleanser + moisturizer for a skin routine) rather than margin optimization alone.
- Use the subscription mechanic to move replenishment-category customers first; expand to habitual-use categories second.

**Don't:**
- Launch a subscribe-and-save at a discount steep enough that subscribers cancel as soon as the price normalizes.
- Bundle low-velocity SKUs with high-velocity ones to move inventory — this dilutes the bundle's use-case clarity.
- Report subscription success by gross subscriber count without the first-renewal retention rate.

## Edge cases / when the rule does NOT apply

For premium one-time purchase categories (luxury, furniture, bespoke), subscription is not a natural LTV lever — focus on referral programs and accessories/complementary products instead. For very early-stage brands without replenishment data, model the cadence from category norms first, then validate with first-cohort data.

## See also

- [`../agents/merchandising-specialist.md`](../agents/merchandising-specialist.md) — owns the bundle and subscription design.
- [`./aov-and-frequency-are-levers-you-design-not-constants.md`](./aov-and-frequency-are-levers-you-design-not-constants.md) — the master rule this operationalizes.

## Provenance

Operationalizes §3 #7 ("AOV and frequency are levers you design, not constants") with the concrete LTV-lens test that separates structural LTV levers from promotional tactics. Standard practice in DTC subscription economics; the cancel-rate and cohort-LTV framing is the team's standing diagnostic approach.

---

_Last reviewed: 2026-06-05 by `claude`_
