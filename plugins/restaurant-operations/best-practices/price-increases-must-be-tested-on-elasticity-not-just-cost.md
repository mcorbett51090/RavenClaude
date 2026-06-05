# Price Increases Must Be Tested on Elasticity, Not Just Cost

**Status:** Pattern
**Domain:** Menu pricing / revenue management
**Applies to:** `restaurant-operations`

---

## Why this exists

When food costs rise, the instinct is to pass the increase to the guest through a uniform menu price hike. This ignores price elasticity: high-traffic, low-average-check items (appetizers, beverages, combo meals) are often more price-sensitive than the headline entrée that guests anchor on. A blanket 8% price increase may protect margin on steak but destroy volume — and thus contribution margin — on the beverages and sides that carry the highest margin dollars. Pricing decisions built solely on cost percentages routinely damage revenue more than they recover it. Elasticity-informed pricing raises prices selectively, on items where guests are least sensitive, and holds or even lowers price on high-traffic volume drivers.

## How to apply

Build the elasticity test before finalizing a price change:

```
Price-elasticity test framework:
1. Segment the menu into elasticity tiers:
   - Anchor items (guests "know" the price — burgers, wings, daily specials): HIGH sensitivity
   - Destination items (guests choose the restaurant for this item): LOW sensitivity
   - Add-ons / beverages (impulse purchase, perceived low price): MEDIUM sensitivity
   - Premium items (steak, seafood — guest expects to pay more): LOW sensitivity

2. For each tier, estimate price sensitivity:
   - If price increases 10%, what % volume decline do you expect?
   - Revenue impact: (new price × expected volume) vs. (old price × current volume)

3. Apply increases selectively:
   - Raise destination and premium items first (guests won't defect)
   - Hold or raise minimally on anchor/traffic-driver items
   - Test beverage pricing on a single daypart before system-wide change

4. Validate 30 days post-change:
   - Track item-level mix shift (POS data by item)
   - Flag any item where volume dropped >15% — that is an elasticity signal
```

**Do:**
- Use 90 days of POS item-level data before and after to measure actual elasticity, not assumed elasticity.
- Engineer the menu at the same time as the price review — a price increase is also an opportunity to retire low-margin, low-volume dogs.
- Communicate price changes to regulars on premium items in advance (loyalty programs, server scripting) — surprise is a larger negative than the price itself.

**Don't:**
- Apply a flat percentage increase across all items — it is the easiest to execute and the highest-risk for volume loss on traffic drivers.
- Raise prices and simultaneously change portions — the guest perceives shrinkflation, which compounds the elasticity effect.

## Edge cases / when the rule does NOT apply

QSR value menus with fixed price tiers ($1/$2/$3) are effectively set by the brand/franchisor and are not subject to operator-level elasticity testing. During a generalized inflationary period where all competitors are raising prices simultaneously, elasticity is lower and a larger uniform increase may be justified — but item-level analysis still improves targeting.

## See also

- [`../agents/menu-cost-engineer.md`](../agents/menu-cost-engineer.md) — owns the pricing analysis and menu engineering matrix that frames the elasticity decision.
- [`../agents/restaurant-finance-analyst.md`](../agents/restaurant-finance-analyst.md) — models the revenue and margin impact of price change scenarios.
- [`./engineer-the-menu-on-margin-and-popularity-never-price.md`](./engineer-the-menu-on-margin-and-popularity-never-price.md) — the matrix that identifies where price sensitivity and margin opportunity intersect.

## Provenance

Price elasticity in restaurant menus is covered in standard revenue management and menu engineering literature (e.g., Kasavana and Smith's menu engineering framework); selective vs. uniform pricing is a core principle in restaurant pricing consulting.

---

_Last reviewed: 2026-06-05 by `claude`_
