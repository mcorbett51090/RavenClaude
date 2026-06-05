# Whales are a concentration risk, not just a revenue line

**Status:** Pattern
**Domain:** Game monetization and live-ops
**Applies to:** `game-development`

---

## Why this exists

In F2P mobile games, it is common for the top 1–5% of paying players to generate 50–80% of IAP revenue [ESTIMATE — varies widely by genre]. Most live-ops teams treat this as a feature: high-value players are served with exclusive bundles, higher spend caps, and dedicated cosmetics. The concentration risk is underweighted. When a small cohort of whales drives a majority of revenue, any event or balance change that damages whale satisfaction can produce a revenue cliff — not a gradual decline — in a single week. Additionally, whale-optimized monetization often damages the experience for mid-spenders and free players, accelerating their churn and eventually shrinking the audience the whales play in. The whale concentration must be tracked as a business risk, not just as a monetization metric.

## How to apply

Track the top-1% and top-5% revenue concentration quarterly. Set a concentration ceiling above which the team flags an active risk.

```
Whale-concentration risk model:

  Metric 1: Revenue concentration ratio
    top1_pct_revenue  = revenue from top 1% of payers / total IAP revenue
    top5_pct_revenue  = revenue from top 5% of payers / total IAP revenue

  Risk thresholds [ESTIMATE — calibrate to your genre]:
    top1 > 40%: CONCENTRATION RISK — single-segment dependency
    top5 > 70%: HIGH CONCENTRATION — revenue cliff on any whale-segment churn event

  Metric 2: Whale churn rate
    = top-1% payers who have not spent in 30 days / active top-1% payers last period

  Risk action: if whale churn rate > 10%/month AND top1 > 40%:
    — Immediate live-ops review: what changed?
    — Sensitivity test: model revenue impact if top-1% spend drops 25%, 50%

  Balance rule: every economy change must be reviewed for whale-segment impact
  before shipping. "Tuning the economy for health" can accidentally nerf the
  whale segment's primary spend motivation (e.g., competitive advantage, exclusive access).
```

**Do:**
- Track revenue concentration as a regular live-ops vital sign alongside D1/D7/D30.
- Review every economy balance change for whale-segment impact before shipping.
- Maintain a distinct mid-spender segment (typically $10–$100/month [ESTIMATE]) as an early-warning indicator — mid-spender health often predicts whale-pipeline health.

**Don't:**
- Optimize new bundles purely for whale conversion without checking the impact on mid-spender and free-player experience.
- Interpret a top-1% concentration above 50% as health — it is a concentration risk.
- Ignore the whale-churn signal in the live-ops dashboard because the total revenue number is still up.

## Edge cases / when the rule does NOT apply

Premium games without IAP have no whale segment in the traditional sense. Subscription-model games (monthly subscription, no IAP) have a different concentration profile — the subscriber-churn rate is the equivalent metric. Battle-pass games with a defined ceiling on spend have lower concentration risk because the per-player spend ceiling compresses the top/bottom distribution.

## See also

- [`../agents/live-ops-analyst.md`](../agents/live-ops-analyst.md) — tracks monetization signals including revenue concentration and whale-segment health.
- [`./design-the-economy-as-a-system-not-a-price-list.md`](./design-the-economy-as-a-system-not-a-price-list.md) — the companion rule on designing the economy so concentration risk is a designed property, not an accident.

## Provenance

Codifies the whale-concentration-risk framing standard in F2P live-ops analysis. The revenue-cliff pattern from a single-segment dependency is the most severe monetization risk in F2P games; most teams that underweighted it discovered it after a balance change or competitive event removed the whale segment's primary motivation.

---

_Last reviewed: 2026-06-05 by `claude`_
