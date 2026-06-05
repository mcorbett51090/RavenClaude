# Creative fatigue is a CAC driver — rotate before it spikes

**Status:** Primary diagnostic
**Domain:** DTC performance marketing
**Applies to:** `ecommerce-dtc`

---

## Why this exists

On paid social, the same creative asset reaches the same audience repeatedly as the audience pool exhausts. Frequency rises, click-through rate falls, and cost-per-click climbs — but the platform's ROAS metric obscures this because it's measuring conversions that may lag by days. By the time the ROAS signal shows a decline, the CAC has been elevated for weeks. Monitoring creative-level frequency and CTR — not just ROAS — is the early-warning signal for fatigue. The cost of missing this is compounding: fatigued creative costs more, generates lower quality traffic, and trains the algorithm toward less-efficient audiences.

## How to apply

Instrument a creative-fatigue dashboard at the ad-creative level (not campaign level). Set frequency and CTR thresholds that trigger a rotation review before ROAS degrades.

```
Creative-fatigue monitoring model:
  Frequency trigger: > 3.0 within a 7-day window on the same audience → rotate
  CTR trend trigger: CTR drops > 30% from the creative's week-1 baseline → review
  CPM trend: CPM increasing > 20% week-over-week with stable bid → audience saturation signal

Creative rotation cadence (approximate):
  Cold audiences: new creative every 2–3 weeks [ESTIMATE]
  Retargeting: new creative every 4–6 weeks (smaller pool, slower fatigue) [ESTIMATE]

Rule: pause fatigued creative before the ROAS signal confirms the decline — the ROAS lag is typically 7–14 days.
```

**Do:**
- Track CTR and frequency at the individual ad creative level, not just campaign level.
- Maintain a creative pipeline of 3–5 tested concepts per top-performing campaign so rotation doesn't require a pause.
- Set automated rules or a weekly creative-review calendar to catch fatigue before it compounds.

**Don't:**
- Rely on ROAS alone as the primary creative-performance signal.
- Keep a creative live past its frequency threshold because it was a previous winner.
- Pause all ad variants simultaneously — stagger rotation to preserve algorithm learning continuity.

## Edge cases / when the rule does NOT apply

For low-budget accounts (under $2k/month) where frequency builds slowly, monthly creative review may be sufficient. Seasonal campaign creative (Black Friday, back-to-school) has a defined flight window — fatigue thresholds are less relevant when the campaign ends in 14 days regardless. UGC and testimonial formats typically fatigue more slowly than branded studio creative.

## See also

- [`../agents/performance-marketing-strategist.md`](../agents/performance-marketing-strategist.md) — owns creative testing and channel efficiency.
- [`./measure-paid-social-incrementally-not-last-click.md`](./measure-paid-social-incrementally-not-last-click.md) — the companion rule on measuring paid social accurately.

## Provenance

Codifies the creative-fatigue monitoring discipline standard in paid social management. Motivated by the pattern where brands with climbing CAC diagnose targeting or bid issues when the real cause is exhausted creative on a saturated audience — the frequency signal is the early indicator the ROAS metric misses.

---

_Last reviewed: 2026-06-05 by `claude`_
