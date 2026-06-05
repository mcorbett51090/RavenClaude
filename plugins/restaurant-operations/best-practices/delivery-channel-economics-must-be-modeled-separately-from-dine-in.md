# Delivery Channel Economics Must Be Modeled Separately from Dine-In

**Status:** Absolute rule
**Domain:** Channel economics / four-wall P&L
**Applies to:** `restaurant-operations`

---

## Why this exists

Third-party delivery platforms (DoorDash, Uber Eats, Grubhub) take 15–30% commission on gross sales [unverified — training knowledge]. A restaurant blending delivery and dine-in revenue into a single P&L sees a food-cost percentage and prime cost that reflects the blended average — and the delivery channel's real economics are invisible. A dine-in sale at $20 contributes ~$8 of contribution margin at a 40% margin; the same $20 through a 25%-commission third-party platform contributes ~$3 after commission, before accounting for packaging cost. Operators who grow delivery volume without modeling it separately can see revenue rise and profit fall simultaneously, misread the cause, and make the wrong interventions.

## How to apply

Build a separate channel P&L for every significant delivery or off-premise channel:

```
Channel P&L model (per channel, per period):
  Channel revenue (gross, platform-reported):        $______
  Platform commission rate:                          ______%
  Net revenue to restaurant (gross − commission):    $______

  Incremental channel costs:
    Packaging (boxes, bags, etc.):                   $______
    Incremental food cost (portion accuracy loss):   $______
    Labor premium for packing / expediting:          $______

  Channel COGS:                                      $______
  Channel contribution (net revenue − channel COGS): $______
  Channel contribution margin %:                     ______%

  Dine-in equivalent margin for comparison:          ______%

  Channel viability test:
    If channel contribution % < variable cost %: channel loses money on every order.
    If channel contribution % < dine-in by >15 points: evaluate whether incremental volume justifies the model.
```

**Do:**
- Pull platform sales data weekly and model the channel P&L at the same cadence as the dine-in P&L.
- Negotiate platform commission rates — most platforms have tiered rate structures that operators rarely request.
- Price delivery menus at a premium (5–15%) to partially offset commission cost — most platforms allow differential pricing.

**Don't:**
- Aggregate delivery and dine-in revenue into a single food-cost calculation; the weighted-average result misleads the diagnosis.
- Grow delivery volume as a "coverage" strategy during low dine-in periods without checking whether the channel contribution is positive.

## Edge cases / when the rule does NOT apply

First-party delivery (operator-owned ordering and delivery) has no platform commission; the model still applies but the commission line is replaced by the direct cost of the delivery fleet/labor. Ghost kitchens operating 100% off-premise have no dine-in comparison benchmark; their entire P&L is the "delivery channel" model.

## See also

- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — owns the channel P&L model and the dine-in vs. delivery margin comparison.
- [`../agents/restaurant-engagement-lead.md`](../agents/restaurant-engagement-lead.md) — flags delivery channel economics during the initial engagement scoping.
- [`./prime-cost-is-the-master-number.md`](./prime-cost-is-the-master-number.md) — delivery channel commission collapses the revenue available for prime cost absorption; model the channel before setting prime-cost targets.

## Provenance

Third-party delivery channel economics and the commission-impact model are documented in restaurant industry research (National Restaurant Association, Technomic, restaurant consulting publications); figures marked `[unverified — training knowledge]`.

---

_Last reviewed: 2026-06-05 by `claude`_
