# Checkout friction is a separate problem from product-page friction

**Status:** Primary diagnostic
**Domain:** DTC conversion funnel
**Applies to:** `ecommerce-dtc`

---

## Why this exists

When conversion rate is low, the natural first instinct is to fix the product page — better copy, more images, social proof. But product-page and checkout friction are distinct problems with different root causes, different fixes, and different data signatures. A brand that patches the product page while the real leak is checkout abandonment wastes the improvement. The funnel diagnostic must separate the two stages before any fix is deployed; the data almost always shows a step-change drop at the add-to-cart, at cart-to-checkout, or at checkout-to-purchase — only one of which lives on the product page.

## How to apply

Pull the funnel at three distinct stages: (1) product page → add to cart, (2) cart → checkout initiated, (3) checkout initiated → purchase complete. Identify which rate is below benchmark before diagnosing the cause.

```
Funnel diagnostic breakpoints:
  Stage 1: Product page → ATC
    Benchmark: 5–8% for cold traffic [ESTIMATE — verify per vertical]
    Drivers if low: product-page copy, images, price, trust signals, social proof

  Stage 2: Cart → Checkout initiation
    Benchmark: 60–75% of carts reaching checkout [ESTIMATE]
    Drivers if low: shipping cost reveal, cart-page friction, account-creation gate

  Stage 3: Checkout initiation → Purchase
    Benchmark: 55–70% of initiated checkouts completing [ESTIMATE]
    Drivers if low: payment options, form length, address validation errors, trust at payment

Diagnosis rule: fix the stage with the largest absolute drop first; don't touch Stage 1 if Stage 3 is the leak.
```

**Do:**
- Map all three funnel stages in the analytics platform before recommending any fix.
- Fix the highest-drop stage before investing in CRO at another stage.
- Separate mobile vs. desktop funnels — checkout abandonment is often disproportionately mobile.

**Don't:**
- Default to "improve the product page" without checking whether the leak is at checkout.
- Diagnose conversion issues at the headline "conversion rate" without stage-level data.
- Recommend A/B tests on product pages if checkout is where the cart empties.

## Edge cases / when the rule does NOT apply

Single-product brands with a direct-to-checkout flow (one-product landing pages with no traditional cart step) collapse Stages 2 and 3 together; treat them as a single post-ATC funnel. Subscription-first funnels that route to a quiz or configurator before the cart add an upstream stage that must be mapped separately.

## See also

- [`../agents/merchandising-specialist.md`](../agents/merchandising-specialist.md) — owns product-page and checkout funnel diagnosis.
- [`./read-the-conversion-funnel-not-the-conversion-rate.md`](./read-the-conversion-funnel-not-the-conversion-rate.md) — the parent rule on reading funnel stages.

## Provenance

Codifies the team's §3 #4 house opinion ("read the conversion funnel, not the conversion rate") with a specific named diagnostic — the product-page vs. checkout separation — that the headline rate obscures. The "fix the product page" default is the most-observed first-fix error in operator-submitted CRO audits.

---

_Last reviewed: 2026-06-05 by `claude`_
