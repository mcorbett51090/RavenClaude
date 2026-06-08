# Sell-through tells you whether to reorder or mark down

**Status:** Pattern
**Domain:** Inventory management, markdown cadence, replenishment
**Applies to:** `retail-store-operations`

---

## Why this exists

A sell-through rate without context is a number. With context — weeks-of-supply remaining,
weeks left in the selling season, and whether the item is seasonal or evergreen — it becomes a
decision. Retailers who skip this check either:

1. **Reorder into already-sufficient inventory** — adding weeks-of-supply when inventory
   is already above the demand curve, deepening the markdown they'll eventually need.
2. **Hold when they should mark down** — carrying inventory past the season's demand peak,
   then taking a deeper markdown than an earlier one would have required.

Sell-through rate + weeks-of-supply + weeks remaining in season = the three inputs that resolve
the reorder-vs.-markdown question for any seasonal or fashion item.

## How to apply

1. Compute sell-through %:

```
Sell-through % = (Units Sold ÷ Units Received) × 100
```

2. Compute weeks-of-supply:

```
WOS = On-Hand Units ÷ Average Weekly Sales
```

3. Compare sell-through to the season target at this point in the calendar. If a 16-week
   season expects 50% sell-through by week 8, and you're at week 8 with 30%, you are
   behind the target curve.

4. Traverse the markdown-or-hold decision tree in
   `knowledge/retail-store-operations-decision-trees.md`.

**Do:**

- Always pair a reorder recommendation with a sell-through rate and WOS figure.
- Always pair a markdown recommendation with a sell-through rate, WOS, and season-weeks-remaining.
- Use `scripts/retail_calc.py` `sell_through` and `weeks_of_supply` modes to confirm arithmetic.
- Set a liquidation floor before the markdown ladder — never mark below it without explicit approval.

**Don't:**

- Recommend a reorder without checking whether WOS is already sufficient.
- Recommend holding when sell-through is significantly below the season target with fewer than
  4 weeks remaining — the markdown will be deeper and less effective later.
- Present a markdown recommendation without a stated sell-through rate and WOS.

## Edge cases / when the rule does NOT apply

- **Evergreen / never-out-of-stock items:** WOS still matters for replenishment, but there is
  no season-end deadline. The markdown trigger is different: a persistently slow mover below
  GMROI threshold, not an imminent season-end.
- **New item introductions:** sell-through in the first 2–3 weeks of a launch may be low due to
  awareness ramp, not demand failure. Set a re-evaluation gate at 4–6 weeks before acting.
- **Promotional events:** a sell-through spike during a promotion does not change the structural
  sell-through trend — strip out promo weeks when computing the baseline.

## See also

- [`./gmroi-not-just-gross-margin.md`](./gmroi-not-just-gross-margin.md)
- [`./planogram-compliance-is-revenue.md`](./planogram-compliance-is-revenue.md)
- [`../knowledge/retail-store-operations-decision-trees.md`](../knowledge/retail-store-operations-decision-trees.md)
- [`../scripts/retail_calc.py`](../scripts/retail_calc.py)

## Provenance

Standard open-to-buy and markdown cadence practice in specialty, apparel, and department store
retail. The sell-through + WOS + season-weeks-remaining framework is the foundation of markdown
optimization models used by most major retailers and is documented in NRF and retail-analyst
publications.

---

_Last reviewed: 2026-06-08 by `claude`._
