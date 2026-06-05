# Set wholesale pricing floors that protect margin under 280E

**Status:** Absolute rule
**Domain:** Cannabis operations / pricing / 280E
**Applies to:** `cannabis-operations`

---

## Why this exists

In a standard retail business, price compression is painful but survivable — the firm can absorb it with lower operating costs. Under 280E, cannabis operators cannot deduct those operating costs, so every dollar of price discount lands directly on a tax-burdened bottom line. A wholesale price set below full-landed-cost-plus-margin leaves an operator paying federal tax on a loss. Distributors and vertically integrated operators are especially exposed because they set the price for both the wholesale and the retail tier; an undiscounted retail margin can mask a wholesale price that is structurally unprofitable before 280E.

## How to apply

Build a pricing floor for each SKU using this structure:

```
Wholesale floor — [SKU] — [state] — effective [date]

1. Direct production cost (COGS-eligible)
   - Raw material cost per unit:         $____
   - Direct labor per unit:              $____
   - Allocated overhead per unit:        $____
   SUBTOTAL — production COGS:           $____

2. Non-COGS operating cost (280E-disallowed)
   - Per-unit freight/distribution:      $____
   - Per-unit sales/admin allocation:    $____
   SUBTOTAL — non-deductible cost:       $____

3. Federal tax gross-up (on the non-COGS portion)
   Effective 280E rate × non-COGS cost:  $____

4. Target wholesale margin:              ____%

MINIMUM WHOLESALE FLOOR PRICE:          $____
```

Review floors quarterly and any time COGS or freight costs shift more than 5%.

**Do:**
- Treat the 280E gross-up as a hard cost, not a variable — it is assessed whether or not the operator earns a net profit.
- Run the floor calculation before entering any promotional agreement that sets volume-based price breaks.
- Document the floor and the supporting build in the same file as the excise-tax calculation.

**Don't:**
- Set wholesale price from a market-average reference without confirming that reference reflects 280E-burdened cost structures.
- Allow sales to override pricing floors without a written exception approved by finance — even temporary promotions compound over a quarter.
- Conflate wholesale margin with taxable income margin; the difference is the 280E-disallowed operating cost.

## Edge cases / when the rule does NOT apply

- Operators in Schedule III reclassification states (if and when federal rescheduling applies) will have different disallowance structures — revisit the floor build if federal tax posture changes.
- Cost-plus transfer pricing for intra-entity moves (cultivation to manufacturing) uses a separate methodology and is not a "sale" subject to this floor.

## See also

- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — builds the cost model the floor depends on.
- [`./280e-makes-cogs-allocation-existential-not-academic.md`](./280e-makes-cogs-allocation-existential-not-academic.md) — the COGS allocation that sets the production cost subtotal.
- [`./excise-tax-is-a-margin-line-item-not-a-pass-through.md`](./excise-tax-is-a-margin-line-item-not-a-pass-through.md) — the excise-tax gross-up sits beside the 280E gross-up in the floor build.

## Provenance

Derived from cannabis operations pricing practice and 280E disallowance mechanics. `[unverified — training knowledge]` — validate the tax gross-up formula with a licensed cannabis CPA before applying to client pricing decisions.

---

_Last reviewed: 2026-06-05 by `claude`_
