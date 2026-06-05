# Schedule Labor to a Sales Forecast, Not Last Week's Actuals

**Status:** Absolute rule
**Domain:** Labor management
**Applies to:** `restaurant-operations`

---

## Why this exists

Scheduling labor from last week's actuals is a trailing indicator — it builds in whatever anomalies, holidays, or events skewed last week and replicates them whether or not they apply this week. A forecast-based schedule uses a rolling sales model (same-day/same-week last year, adjusted for known events) and maps labor to expected covers or transaction volume by daypart. The gap between trailing and forecast scheduling consistently produces a 1–3 labor-point swing. At a $50,000 weekly sales unit, a 2-point swing is $1,000/week — $52,000/year — from a scheduling methodology change alone.

## How to apply

Build a daypart sales forecast before writing the schedule:

```
Daypart labor forecast template (per day):
  Prior-year same-day sales (adjusted for YoY trend):    $______
  Add/subtract: known events, promotions, weather:       $______
  Forecast sales:                                        $______

  Target labor % by daypart:
    Breakfast/AM (if applicable):  _____%  → labor hours: ______
    Lunch:                         _____%  → labor hours: ______
    Dinner:                        _____%  → labor hours: ______
    Late/close:                    _____%  → labor hours: ______

  Total scheduled labor hours:     ______
  Total scheduled labor cost:      $______
  Projected labor %:               ______% (target: segment-specific floor)
```

Build the forecast first, then fill the schedule to it — not the reverse. Reschedule in-week when an unexpected sales swing occurs; don't wait until the week is over to see the labor point.

**Do:**
- Use same-period prior-year data as the base; same-week-last-year is more predictive than same-week-last-month.
- Include a "known event" adjustment column — a local festival, a competitor closure, a rain weekend all move the forecast.
- Verify actual vs. forecast labor % daily during the shift; adjust the remaining crew accordingly.

**Don't:**
- Copy last week's schedule unless last week was a representative, event-free week — it almost never is.
- Schedule labor to an optimistic forecast; use the midpoint of the prior-year range, not the best day in the period.

## Edge cases / when the rule does NOT apply

Grand-opening weeks and post-remodel reopenings have no comparable prior-year period; use a build-up model from expected cover counts. Ghost kitchens and off-premise-only operations have a flatter demand curve; the forecast logic applies, but daypart granularity may be less meaningful.

## See also

- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns the daypart scheduling and labor-to-demand alignment.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the four-wall labor-% read and weekly scorecard.
- [`./labor-is-a-ratio-to-sales-with-a-floor.md`](./labor-is-a-ratio-to-sales-with-a-floor.md) — the floor constraint that governs the minimum schedule this forecast can produce.

## Provenance

Standard restaurant labor management practice; forecast-based scheduling vs. historical replication is the foundational distinction in restaurant labor cost consulting and scheduling-system design.

---

_Last reviewed: 2026-06-05 by `claude`_
