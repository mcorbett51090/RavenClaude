---
scenario_id: 2026-06-05-subscription-churn-vs-acquisition
contributed_at: 2026-06-05
plugin: ecommerce-dtc
product: retention
product_version: "n/a"
scope: likely-general
tags: [subscription, churn, retention, ltv, discount-only]
confidence: medium
reviewed: false
---

## Problem

A supplements brand was acquiring subscription customers hard but its subscriber base wasn't growing — new subs in roughly equaled churned subs out. The reflex was "acquire more," but pouring acquisition into a leaky subscription is filling a bucket with a hole: every point of monthly churn compounds against LTV, and past a certain churn rate no acquisition budget keeps the base growing profitably. Retention is the profit engine (§3 #3); the second purchase — here, the second *charge* — is everything.

## Context

- Segment: supplements (a replenishment category, the kind subscriptions *should* work for), ~$8M/yr, subscribe-and-save the primary offer.
- Constraint: the subscription was **discount-only** — the sole reason to subscribe was the price break, so it attracted deal-seekers who churn the moment a better promo appears (a discount is the floor of a subscription value layer, not the ceiling). Supplements/replenishment churn should run ~4–8% monthly; discovery-style boxes run 10–15% [verify-at-use]. This brand was at the high end for its category.
- Nobody had split **voluntary churn** (customer cancels) from **involuntary churn** (failed payment / expired card) — involuntary is typically 25–40% of total churn and is a *billing* fix, not a value problem [verify-at-use].

## Attempts

- Tried: **split the churn before treating it** — voluntary vs. involuntary. Outcome: a meaningful slice was involuntary (failed payments), recoverable with **dunning / card-updater** (dunning can cut payment-related churn ~30–50% in the first month) [verify-at-use] — the single highest-ROI fix, and it touches no acquisition spend.
- Tried: read churn against the **win-back window** — re-engagement gets sharply harder after the lapse stretches out (see [`../best-practices/the-win-back-window-closes-at-180-days-act-before-it.md`](../best-practices/the-win-back-window-closes-at-180-days-act-before-it.md)) — and stood up a post-purchase/lifecycle flow *before* scaling acquisition (see [`../best-practices/build-a-post-purchase-sequence-before-scaling-acquisition.md`](../best-practices/build-a-post-purchase-sequence-before-scaling-acquisition.md)).
- Tried: added a **value layer beyond the discount** — replenishment convenience, member-only access, flexible cadence, easy skip/pause (the "skip" that prevents a cancel) — so the subscription survives when a competitor also discounts. Price increases are the #1 cited reason for subscriber loss (~71% in one survey), so the value layer is the hedge against the next price move [verify-at-use].
- Tried: explicitly held acquisition flat until churn moved — adding subscribers to a base churning at the high end of its category band is negative-leverage spend.

## Resolution

The fix was **retention-first, not acquisition-first**: dunning recovered the involuntary churn, a skip/pause-and-flexible-cadence value layer cut the voluntary churn, and a lifecycle flow caught lapsing subs inside the win-back window. With churn down, the *same* acquisition spend grew the base — because the bucket stopped leaking. The brand reframed the subscription from a discount mechanic to a value relationship.

**Action for the next consultant hitting this pattern:** **fix churn before scaling acquisition on a subscription** (§3 #3). Split voluntary vs. involuntary (dunning is the cheapest win), build a value layer past the discount so deal-seekers aren't the whole base, and act inside the win-back window. A discount-only subscription is a churn machine at scale — see [`../knowledge/ecommerce-decision-trees.md`](../knowledge/ecommerce-decision-trees.md) "Subscription vs one-time purchase" and [`../skills/build-the-retention-engine/SKILL.md`](../skills/build-the-retention-engine/SKILL.md). The [`../scripts/dtc_calc.py`](../scripts/dtc_calc.py) `ltv-cac` mode shows how a churn change moves LTV against the CAC line.

**Sources (retrieved 2026-06-05):**
- Recurly — Customer churn benchmarks by industry (involuntary 25–40% of churn; dunning recovery): https://recurly.com/research/churn-rate-benchmarks/
- Eightx — Average subscription churn rate by category 2026 (replenishment 4–7%, discovery 10–15%): https://eightx.co/blog/average-subscription-churn-rate-by-category
- Recharge — Subscription metrics every DTC brand should track: https://getrecharge.com/blog/10-subscription-metrics-every-dtc-brand-should-track/

Churn benchmarks are highly category-dependent — treat every figure as `[verify-at-use]` and recompute against the brand's own cohort churn curves and voluntary/involuntary split (§3 #8).
