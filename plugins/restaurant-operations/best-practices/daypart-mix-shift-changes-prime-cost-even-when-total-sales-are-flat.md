# Daypart Mix Shift Changes Prime Cost Even When Total Sales Are Flat

**Status:** Primary diagnostic
**Domain:** Restaurant operations / P&L analysis
**Applies to:** `restaurant-operations`

---

## Why this exists

A restaurant operator who sees flat total sales but rising prime cost typically looks for a price or rate problem — food cost went up, or labor rates increased. Often the real cause is a daypart mix shift: the mix of revenue across breakfast, lunch, dinner, and late-night changed, and the dayparts have structurally different prime costs. A dinner-heavy restaurant that loses 10% of its dinner sales to lunch (which runs higher labor % and lower check average) will see prime cost rise even if every daypart's individual cost structure is unchanged. Diagnosing prime cost from total sales without daypart breakout misses this category of problem entirely.

## How to apply

Run the daypart decomposition before concluding that food or labor rates are the problem:

```
Daypart Mix Analysis — [Location] [Period]
──────────────────────────────────────────
                    │ Breakfast │  Lunch  │  Dinner  │ Late-night │  Total
────────────────────┼───────────┼─────────┼──────────┼────────────┼────────
Net sales ($)       │           │         │          │            │
% of total sales    │           │         │          │            │ 100%
Avg check ($)       │           │         │          │            │
Covers              │           │         │          │            │
────────────────────┼───────────┼─────────┼──────────┼────────────┼────────
Food cost %         │           │         │          │            │
Labor cost %        │           │         │          │            │
Prime cost %        │           │         │          │            │

Prior period mix:
% of total sales    │           │         │          │            │ 100%
Prime cost %        │           │         │          │            │

Mix shift (pp)      │           │         │          │            │ 0%
Prime cost impact   │           │         │          │            │ = Σ(mix shift × daypart prime cost %)
```

**Interpretation guide:**

| Finding | Diagnosis | Action |
|---|---|---|
| High-margin daypart shrinking as % of sales | Mix shift is the prime cost driver | Fix the revenue mix problem (marketing, hours, staffing) |
| Each daypart's prime cost % rose equally | Rate problem (food price or labor rate) | Address ingredient cost or wage rates |
| One daypart's prime cost % rose, others flat | Operational issue in that daypart | Audit that daypart's scheduling or recipe compliance |
| Covers flat but sales per cover declining | Average check erosion (mix or discounting) | Audit item mix and comp/void rate |

**Do:**
- Report prime cost by daypart on a weekly basis alongside the total-store prime cost — the daypart breakdown is where the diagnosis lives.
- Normalize labor for daypart volume before comparing across periods — a higher labor % in a low-volume Tuesday lunch is structurally different from the same rate on a Saturday dinner rush.
- When a daypart's sales mix shifts by more than 3 percentage points vs. the prior period, flag it before the prime cost analysis; the mix shift is likely the cause.
- Include off-premise / delivery as a separate "daypart" if it represents more than 10% of sales — delivery economics are structurally different from dine-in.

**Don't:**
- Compare prime cost % across restaurants without controlling for their daypart mix — a QSR with 80% lunch sales and a full-service restaurant with 80% dinner sales cannot be benchmarked on the same prime cost target.
- Attribute a daypart mix shift to a menu or operations problem without checking whether the root cause is an hours/traffic pattern change (a street closure, a new competitor, a marketing campaign expiration).
- Report a total-store prime cost improvement as a success if it was driven entirely by a favorable mix shift — the underlying daypart economics may not have improved.

## Edge cases / when the rule does NOT apply

Single-daypart concepts (breakfast-only, lunch counter, late-night bar) do not have a mix shift risk by definition. Ghost kitchens and catering operations whose entire output is a single channel also do not have a daypart dimension; their equivalent diagnostic is channel mix (dine-in vs. delivery vs. catering).

## See also
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the four-wall P&L and prime cost bridge analysis.
- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns labor scheduling by daypart.
- [`../knowledge/restaurant-unit-economics.md`](../knowledge/restaurant-unit-economics.md) — covers prime cost benchmarks and the margin bridge.

## Provenance

Standard multi-unit restaurant analysis technique; the daypart decomposition of prime cost is a core diagnostic in restaurant finance consulting and is taught in the Cornell School of Hotel Administration restaurant management curriculum [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
