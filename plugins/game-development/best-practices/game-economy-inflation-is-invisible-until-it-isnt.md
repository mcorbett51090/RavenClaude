# Game economy inflation is invisible until it isn't

**Status:** Primary diagnostic
**Domain:** Game economy design
**Applies to:** `game-development`

---

## Why this exists

A game economy inflates when currency sources outpace sinks. In the early months after launch, the inflationary pressure is invisible: the most dedicated players have accumulated more currency than they need, but the average player hasn't noticed yet. Then one of two things happens: (1) the economy tips into full inflation, where players have so much currency that the hardest content or the most desirable cosmetics feel trivially cheap — and monetization collapses; or (2) the team notices the accumulation and introduces aggressive sinks that feel like a nerf — and the community revolts. Neither is survivable at scale. The signal is visible in the source-to-sink ratio weeks or months before it becomes a player-felt problem; teams that aren't tracking it discover it too late.

## How to apply

Instrument the game economy with a source-to-sink ratio and track it as a live-ops vital sign alongside retention and ARPDAU.

```
Economy health monitoring:

  Core metric: source_to_sink_ratio
    = total_currency_generated_per_day / total_currency_spent_per_day
    Target: maintain within 0.9–1.1 (within 10% of balance)
    Danger zone: ratio > 1.2 for 14+ consecutive days = inflationary signal

  Segment the ratio by player cohort:
    — New players (first 7 days)
    — Active mid-game players (8–90 days)
    — Long-term players (90+ days)
    A ratio > 1.3 in long-term players AND < 0.9 in new players = the classic "endgame inflation / early game grind" split

  Leading indicator: median currency balance trend
    If median currency balance is growing > 5%/week among mid-game players for 4+ weeks:
    investigate the ratio — accumulation is building before it becomes a community perception

  Corrective actions by severity:
    Mild (ratio 1.1–1.2 over < 30 days): add a temporary high-value sink (limited-time offer, event currency drain)
    Moderate (ratio > 1.2 over 30+ days): redesign a recurring sink or reduce a source
    Severe (ratio > 1.5 or community reporting "I have too much of X"): emergency economy review;
      any sink introduced now will feel like a nerf — PSA + gradual introduction required
```

**Do:**
- Track source-to-sink ratio as a live-ops dashboard metric from day one of live-service operation.
- Set automated alerts when the ratio exits the 0.9–1.1 band for 7+ consecutive days.
- Discuss economy balance as a regular agenda item in live-ops reviews, not just when problems surface.

**Don't:**
- Wait for player complaints or monetization drop-off to investigate economy health.
- Introduce large emergency sinks after the community has already accumulated — the community experience is a nerf, not a feature.
- Treat the source-to-sink ratio as a global number only — segment by player cohort to find the split.

## Edge cases / when the rule does NOT apply

Games without a virtual economy (e.g., narrative games, pure premium titles) don't have a source-sink monitoring problem. Games with a fully closed battle-pass economy (currency earned only spent on the current pass with expiry) have structural deflation by design; the monitoring concern shifts to acquisition rate, not accumulation.

## See also

- [`../agents/live-ops-analyst.md`](../agents/live-ops-analyst.md) — tracks the live-ops vital signs including the economy balance metrics.
- [`./design-the-economy-as-a-system-not-a-price-list.md`](./design-the-economy-as-a-system-not-a-price-list.md) — the companion design rule on building the economy with explicit sources and sinks from the start.

## Provenance

Codifies the economy-inflation monitoring discipline from the team's §3 #5 house opinion ("design the economy as a system"). The invisible-until-it-isn't inflation pattern is the most common live-ops economy failure; the source-to-sink ratio is the standard early-warning metric.

---

_Last reviewed: 2026-06-05 by `claude`_
