# Store Page Conversion Rate Is the Pre-Install Funnel

**Status:** Primary diagnostic
**Domain:** Game development — user acquisition, live-ops
**Applies to:** `game-development`

---

## Why this exists

Most studios optimize heavily for D1/D7 retention after install but give the store page a single pass at launch and never revisit it. The store page conversion rate (page visitors who install) is the top of the acquisition funnel — a 1-point improvement in conversion across a meaningful daily impression count can halve effective CPI and improve ROI on paid UA spend without touching the game itself. On mobile, industry average store page conversion rates range approximately 25–35% for organic search and 5–15% for paid UA traffic; significant variation exists by genre. [unverified — training knowledge] A declining conversion rate is often the first signal that the store creative is stale relative to the competitive set or that a recent update changed the game experience in a way that isn't reflected in the store assets.

## How to apply

**Baseline metrics to track weekly:**

```
Store Page Conversion Rate = Installs / Store Page Views × 100

Track separately:
- Organic (search + browse)
- Paid UA (by campaign source where data is available)
- Feature placement (if applicable)

Segment: iOS App Store vs. Google Play (conversion rates differ)
```

**Diagnostic thresholds:**

| Conversion Rate | Signal | Response |
|---|---|---|
| > 35% (organic) | Strong — monitor | Maintain creative freshness; A/B test icon quarterly |
| 25–35% (organic) | Baseline — watch trend | Review if trend is declining over 4+ weeks |
| 15–25% (organic) | Below benchmark | Run icon/screenshot A/B test; audit first-5-second preview video |
| < 15% (organic) | Active problem | Full creative refresh; compare store assets to current top competitors in genre |

**A/B test priority order (by impact):**
1. **Icon** — highest single-asset impact on conversion; test before any other asset.
2. **First screenshot** — the screenshot visible without scrolling on the store card.
3. **Preview video** — first 5 seconds determine watch completion; test the hook frame.
4. **Short description / subtitle** — the copy visible before "read more."
5. **Screenshot order** — test whether feature-focused or gameplay-focused screenshots convert better.

**Creative refresh cadence:**
- Icon: review quarterly against the current top 10 in-genre charts.
- Screenshots: refresh when a major content update changes the visual identity of the game.
- Preview video: refresh at each major version or seasonal update.

**Do:**
- Run store page A/B tests using the platform's native testing tool (Google Play experiments, App Store product page optimization) — these use real traffic and are statistically clean.
- Separate organic conversion from paid UA conversion — a paid UA creative problem will manifest as a low paid conversion rate without affecting organic.
- Track conversion rate as a weekly dashboard metric alongside D1 retention.

**Don't:**
- Make a store page creative change without an A/B test — a bad icon swap can drop conversion 10+ points overnight.
- Attribute a conversion drop entirely to the store page before checking whether an algorithm change affected your organic ranking (lower-quality traffic converts lower even with the same creative).
- Use screenshots from the game's first year if the visual quality or UI has improved significantly — outdated screenshots undersell the current product.

## Edge cases / when the rule does NOT apply

Steam (PC) operates with a different storefront model — wishlist-to-purchase conversion and the capsule image are the analogous metrics. The diagnostic logic is the same but the benchmarks and testing tools differ. This rule as written applies to mobile app stores.

## See also
- [`../agents/live-ops-analyst.md`](../agents/live-ops-analyst.md) — tracks the full acquisition and retention funnel including store conversion.
- [`../agents/gamedev-producer.md`](../agents/gamedev-producer.md) — owns the release and update calendar that determines creative refresh timing.

## Provenance

Codifies standard mobile UA and ASO (App Store Optimization) practice; benchmarks are [unverified — training knowledge] and must be validated against genre-specific data from the studio's own analytics and platform reporting.

---

_Last reviewed: 2026-06-05 by `claude`_
