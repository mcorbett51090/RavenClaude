# Measure paid social incrementally, not last-click

**Status:** Pattern
**Domain:** DTC performance marketing
**Applies to:** `ecommerce-dtc`

---

## Why this exists

Last-click attribution systematically overcredits paid social and undercredits the organic, email, and direct channels that actually closed the sale. A customer who saw an Instagram ad, read an email, then searched the brand and purchased gets assigned to the last-click channel — often brand search or direct — making Meta look inefficient even when it seeded the conversion. The inverse is also common: Meta claims the conversion because its pixel saw the event, while ignoring that the buyer had been on the email list for 60 days. Operating on last-click data leads to misallocation of ad spend and a false picture of which channels are actually growing the customer base.

## How to apply

Run incrementality measurement for paid social at minimum quarterly — a geo-holdout test or a conversion-lift study — to establish the true incremental ROAS. Use this as the primary signal for budget allocation, and use last-click data only as a directional proxy between lift tests.

```
Incrementality test design (geo-holdout):
  1. Split markets into test (ads running) and holdout (ads paused or suppressed).
  2. Run for minimum 2 weeks, ideally 4.
  3. Measure: revenue_test_geo / baseline_test_geo
              vs. revenue_holdout_geo / baseline_holdout_geo
  4. iROAS = incremental revenue ÷ test spend
  5. Compare iROAS to platform-reported ROAS — the gap is the attribution inflation.

Minimum n: ~$10k+ spend per test arm to reduce noise [ESTIMATE].
```

**Do:**
- Run at least one geo-holdout or platform-native lift study per paid social channel per year.
- Report iROAS (incremental) alongside platform ROAS in every channel efficiency review.
- Adjust budget allocation based on iROAS, not platform-reported ROAS.

**Don't:**
- Pause a paid social channel solely because its last-click ROAS dropped — check incrementality first.
- Treat platform-reported ROAS and incremental ROAS as interchangeable.
- Run incrementality tests during peak seasonal periods where confounders dominate.

## Edge cases / when the rule does NOT apply

Brands spending less than $5k/month on paid social don't have the volume to run statistically sound geo-holdout tests; at that scale, directional platform data plus a blended MER (Marketing Efficiency Ratio: total revenue ÷ total ad spend) is the appropriate proxy. Performance max and broad-match campaigns on Google may require separate incrementality treatment.

## See also

- [`../agents/performance-marketing-strategist.md`](../agents/performance-marketing-strategist.md) — owns channel measurement and budget allocation.
- [`./cac-is-a-blended-lie-read-it-by-channel-and-by-cohort.md`](./cac-is-a-blended-lie-read-it-by-channel-and-by-cohort.md) — the companion rule on why blended channel metrics mislead.

## Provenance

Codifies the incrementality-testing discipline standard in growth-stage DTC, motivated by the widespread error of using platform-reported attribution as a channel-efficiency signal. The geo-holdout methodology is the industry-standard approach for paid social incrementality measurement.

---

_Last reviewed: 2026-06-05 by `claude`_
