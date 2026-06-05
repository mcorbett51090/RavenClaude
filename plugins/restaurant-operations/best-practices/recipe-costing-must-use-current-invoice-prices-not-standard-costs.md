# Recipe Costing Must Use Current Invoice Prices, Not Standard Costs

**Status:** Absolute rule
**Domain:** Food cost / menu engineering
**Applies to:** `restaurant-operations`

---

## Why this exists

Standard or "book" recipe costs are updated infrequently and drift from reality every time a supplier invoice changes. A recipe costed 18 months ago at $0.48 for a portion of avocado may cost $0.72 today — a 50% variance that, multiplied across a menu of 80 items, can move actual food cost 2–4 points above theoretical without any waste or portioning error. Operators who diagnose a food-cost gap as a theft or portioning problem when the real cause is a stale cost sheet waste time and morale fixing the wrong thing. Current invoice prices are the only prices that produce a defensible theoretical food cost.

## How to apply

Build a recipe costing cadence tied to invoice activity:

```
Recipe cost update trigger checklist:
  [ ] New supplier contract or pricing agreement → update affected recipes within 5 business days
  [ ] Any ingredient price change of ≥5% on invoice → update immediately
  [ ] Quarterly full-recipe cost review (all items) → scheduled, assigned, with a due date
  [ ] New menu item → costed before it goes live, not after

Per-item costing formula:
  Item cost = Σ (ingredient quantity × current cost per unit × yield factor)
  Food cost % = item cost / menu price
  Contribution margin = menu price − item cost
```

Yield factors must be attached to each ingredient and validated against actual prep yields, not manufacturer specs.

**Do:**
- Tie the recipe-costing system to your POS and supplier invoice system; when an invoice price changes, the system should flag affected recipes automatically.
- Conduct a quarterly "cost audit" for the top 20% of items by volume — those items account for ~80% of total food cost exposure.
- Report theoretical food cost from current-priced recipes weekly; the gap between actual and current-theoretical is the true operational gap.

**Don't:**
- Use "last month's" or "standard" costs in the recipe book when invoices have changed — the theoretical calculation is only as good as the prices feeding it.
- Allow new menu items to go live without a fully costed recipe; the first week of a new item is often the highest-waste, highest-portioning-error week.

## Edge cases / when the rule does NOT apply

Fixed-price contracts with suppliers (locked for 6–12 months) can legitimately use a fixed cost within the contract window — but flag the contract expiration in the recipe system so the update is triggered at renewal. Commodity-indexed ingredients (beef, seafood, produce) may warrant weekly cost updates; the standard quarterly cadence is a minimum.

## See also

- [`../agents/menu-cost-engineer.md`](../agents/menu-cost-engineer.md) — owns recipe costing, theoretical food cost calculation, and the menu cost sheet.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — reads the actual-vs-theoretical gap in the four-wall P&L.
- [`./food-cost-is-judged-against-theoretical-not-last-month.md`](./food-cost-is-judged-against-theoretical-not-last-month.md) — the parent rule; current-invoice costing is the discipline that makes the theoretical calculation valid.

## Provenance

Standard restaurant food-cost management practice; the stale-standard-cost trap is a documented failure mode in restaurant consulting and food-cost audit work.

---

_Last reviewed: 2026-06-05 by `claude`_
