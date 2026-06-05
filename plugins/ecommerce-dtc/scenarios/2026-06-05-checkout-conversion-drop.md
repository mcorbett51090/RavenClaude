---
scenario_id: 2026-06-05-checkout-conversion-drop
contributed_at: 2026-06-05
plugin: ecommerce-dtc
product: merchandising-conversion
product_version: "n/a"
scope: likely-general
tags: [conversion, checkout, cart-abandonment, funnel, mobile]
confidence: medium
reviewed: false
---

## Problem

A brand's overall conversion rate dropped and the founder's instinct was "the traffic got worse — buy better traffic." But a falling *headline* conversion rate is a symptom with at least three different diseases — bad traffic quality, a product-page problem, or a checkout problem — and treating it as one (spending more on acquisition) pours money into a leaking funnel. Read the funnel, not the rate (§3 #4): the stage where users drop names the disease.

## Context

- Segment: home-goods, ~$4M/yr, mostly mobile traffic.
- Constraint: the brand watched a single blended conversion number (average DTC stores convert ~1.4–1.8%; good ~2.5–3%; top decile ~4.7%) and had **no stage-level funnel instrumentation** — sessions → product-page view → add-to-cart → checkout-start → purchase. Without the stages, "conversion dropped" is unactionable.
- Mobile was the majority of sessions, and mobile checkout abandons far harder than desktop (mobile cart abandonment ~85% vs. desktop ~70%) [verify-at-use] — so a mobile-specific checkout regression can sink the blended number even when product-page engagement is fine.

## Attempts

- Tried: **mapped the funnel by stage and found the drop-off** (§3 #4) before touching traffic. Outcome: product-page → add-to-cart was healthy; the cliff was at **checkout-start → purchase**, concentrated on mobile — a checkout problem, not a traffic or PDP problem.
- Tried: separated **checkout friction from product-page friction** — they are different problems with different owners (see [`../best-practices/checkout-friction-is-a-separate-problem-from-product-page-friction.md`](../best-practices/checkout-friction-is-a-separate-problem-from-product-page-friction.md)). The PDP was converting to cart; the loss was downstream, so PDP "optimization" would have been wasted effort.
- Tried: attacked the **#1 documented abandonment cause — unexpected extra costs (shipping/taxes shown only at checkout)**, cited by ~48% of abandoners and the top reason for six straight years [verify-at-use]. Surfacing shipping earlier (and testing a free-shipping threshold set *above* current AOV) addresses the cause at the source. Secondary causes addressed: forced account creation (offer guest checkout), and a long/multi-field mobile checkout (cognitive overload kills mobile conversion).
- Tried: a cart-abandonment email/SMS recovery flow — but as **recovery of a structural ~70% abandonment baseline**, not as the fix for the regression (the regression fix was the cost-transparency + mobile-checkout simplification).

## Resolution

The drop was a **mobile checkout regression**, not bad traffic. Surfacing shipping cost before the final step, enabling guest checkout, and collapsing the mobile checkout fields recovered the checkout-start → purchase rate; the blended conversion number recovered without spending a dollar more on acquisition. The brand kept stage-level funnel instrumentation so the next "conversion is down" question starts with *which stage*.

**Action for the next consultant hitting this pattern:** **diagnose the funnel stage before prescribing — never spend on traffic to fix a checkout leak** (§3 #4). Read sessions → PDP → cart → checkout-start → purchase, locate the cliff, and attribute it to traffic / product page / checkout. If it's checkout, attack unexpected costs (the perennial #1 cause), forced account creation, and mobile field-count first. See [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md) "Conversion is low" and [`../skills/diagnose-the-funnel/SKILL.md`](../skills/diagnose-the-funnel/SKILL.md).

**Sources (retrieved 2026-06-05):**
- Baymard Institute — Cart & checkout abandonment rate (~70%) + reasons (unexpected cost ~48%, forced account, long checkout): https://baymard.com/lists/cart-abandonment-rate
- ZeroCart — Baymard stats decoded, device split (mobile ~85% vs desktop ~70%): https://zerocartai.com/blog/cart-abandonment-statistics-2025
- Swell — DTC ecommerce + checkout statistics (conversion benchmarks): https://www.swell.is/content/custom-checkout-statistics

Abandonment and conversion benchmarks are device- and segment-dependent — treat as `[verify-at-use]` and recompute against the brand's own stage-level analytics before any deliverable (§3 #8).
