# Throughput Is the QSR Margin Variable, Not Just Labor

**Status:** Absolute rule
**Domain:** QSR operations / FOH throughput
**Applies to:** `restaurant-operations`

---

## Why this exists

In QSR and fast-casual operations, labor cost gets managed as the primary margin variable. It is the second-order variable. The first-order variable is throughput — transactions per labor hour or covers per hour. A QSR that serves 80 covers per hour with 12 labor hours has a $0.15/cover labor cost; the same unit serving 55 covers with the same 12 hours has a $0.22/cover labor cost — 47% higher — without a single wage change. Every throughput bottleneck is a labor efficiency collapse. Labor-hour cuts in a throughput-constrained operation remove capacity, reduce throughput further, and make labor cost per cover worse.

## How to apply

Build the throughput model before any labor intervention:

```
Throughput efficiency model (per daypart):
  Covers / transactions served:           ______
  Labor hours on shift:                   ______
  Covers per labor hour:                  ______  (transactions / hours)
  Target covers per labor hour:           ______  (segment-specific; varies by format)

  Bottleneck diagnostic:
    Time order to payment (speed of service): ______ seconds/minutes
    Queue length at peak:                     ______ (in-store or drive-through)
    Remakes / re-fires per 100 orders:        ______% (signal of production bottleneck)
    Drive-through pull-forward rate:          ______% (signal of order-completion bottleneck)

  Revenue impact of bottleneck:
    Lost transactions (estimated) per hour of constraint: ______
    × average ticket:                                     $______
    Revenue leakage per peak hour:                        $______
```

Throughput levers in order of cost:
1. **Position deployment** — wrong position staffed at peak (e.g., expediter absent) costs more in throughput than the wage saves.
2. **Order accuracy** — a 5% remake rate at 90 seconds/remake steals 4.5 minutes of throughput per 100 orders.
3. **Equipment spacing and line flow** — a production line with a travel bottleneck can't be staffed around.
4. **Technology** (mobile ordering, digital boards) — reduces ordering time and frees position capacity.

**Do:**
- Measure speed of service (SOS) and throughput by daypart daily, not just in mystery shops or quarterly audits.
- Diagnose the bottleneck before cutting labor — removing a position that is not the bottleneck does nothing for throughput and everything for overtime elsewhere.
- Model the incremental revenue available from removing the constraint before the capex/training investment.

**Don't:**
- Cut labor hours at peak to manage weekly labor % without checking whether the reduction hits the throughput floor.
- Treat SOS and throughput as brand standards rather than financial metrics — they are both.

## Edge cases / when the rule does NOT apply

Fine dining and full-service segments have no throughput optimization objective at the table level — the rule is specific to QSR, fast-casual, and counter-service formats. Off-peak periods with low traffic have excess capacity, not a throughput constraint; throughput analysis is peak-only.

## See also

- [`../agents/foh-boh-operations-specialist.md`](../agents/foh-boh-operations-specialist.md) — owns the speed-of-service diagnosis and throughput improvement plan.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the revenue-leakage model and the per-cover labor cost calculation.
- [`./labor-is-a-ratio-to-sales-with-a-floor.md`](./labor-is-a-ratio-to-sales-with-a-floor.md) — the throughput floor IS the service floor; the two rules define the same constraint from opposite sides.

## Provenance

Throughput as the primary QSR operating variable is foundational in QSR operations management; the covers-per-labor-hour framing is standard in fast-food operations consulting and franchise performance benchmarking.

---

_Last reviewed: 2026-06-05 by `claude`_
