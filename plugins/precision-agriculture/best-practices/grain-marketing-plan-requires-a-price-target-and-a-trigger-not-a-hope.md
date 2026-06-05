# Grain Marketing Plan Requires a Price Target and a Trigger, Not a Hope

**Status:** Absolute rule
**Domain:** Precision agriculture / grain marketing
**Applies to:** `precision-agriculture`

---

## Why this exists

The most common and costly marketing failure in grain farming is the absence of a written plan. A grower who sells at harvest when cash flow demands — rather than when the market provides — is not marketing: they are surrendering to circumstance. A grain marketing plan does not require perfect foresight; it requires a breakeven price, a target price that covers cost plus a margin goal, and a written trigger (price level, basis level, or date) that forces execution. Without a trigger, a good price comes and goes while the grower waits for better. The cost is real: even a 10-cent/bushel improvement on 50,000 bushels is $5,000 — every year.

## How to apply

Build the marketing plan before planting, update it at key crop stages (planting completion, pollination, harvest start), and execute against it:

```
Grain Marketing Plan — [Crop] [Marketing Year]
──────────────────────────────────────────────
Farm/operation: ___________
Bushels to market (expected):  ___  bu
Breakeven price (cost of production ÷ APH):  $___/bu
Target price (breakeven + margin goal):  $___/bu

Pre-harvest sales (new-crop futures or HTA):
  Tranche 1: ___% of expected production  at  $___/bu  trigger: [price / date]
  Tranche 2: ___% of expected production  at  $___/bu  trigger: [price / date]
  Tranche 3: ___% at harvest or post-harvest, basis target: ___¢ over/under [delivery month]

Storage decision rule:
  Store only if:  (a) basis is currently weak AND (b) storage cost/month < expected basis gain
  Storage cost (commercial):  ___¢/bu/month
  Carry in the market:  ___¢/bu/month  (source + date: ___)
  Decision:  [ ] Carry is paying — store  [ ] Carry is not paying — sell

Basis target for stored bushels:  ___¢ over/under [delivery month]
Basis sell trigger:  when basis reaches ___¢ OR by [date], whichever comes first.

Hedge / options overlay (if used):
  Put floor:  strike $___  premium $___/bu  net floor: $___
  Call ceiling:  strike $___  premium $___/bu
```

**Do:**
- Set the breakeven first, before any marketing decision — a price that feels "low" relative to the market but is above breakeven is profitable.
- Write the triggers before planting — the market will not be at the target price when you finally have time to think about it.
- Pre-sell in tranches (30–40% at planting, 30% mid-season, hold remainder) to average price risk rather than trying to time the top.
- Distinguish new-crop and old-crop marketing plans; they have different basis behavior and different cash-flow needs.

**Don't:**
- Hold all grain hoping for higher prices without a written sell trigger — hope is not a marketing strategy.
- Sell 100% at harvest without modeling whether carry is paying; storage can be profitable when basis is inverted relative to the carry market.
- Quote a futures price as the realized price — always include the local basis in the expected price calculation.

## Edge cases / when the rule does NOT apply

A grower under contract at a fixed price for the entire crop (forward contract at planting) has already made the marketing decision; the plan governs uncontracted bushels. Specialty crops (seed corn, non-GMO, organic) with contracted premiums follow the contract terms; basis and futures analysis applies only to the spot/open market portion.

## See also
- [`../agents/ag-market-analyst.md`](../agents/ag-market-analyst.md) — owns basis tracking, futures analysis, and marketing plan construction.
- [`../agents/farm-operations-analyst.md`](../agents/farm-operations-analyst.md) — owns the cost-of-production breakeven that anchors the price target.
- [`./basis-is-the-local-price-gap-that-the-grower-controls.md`](./basis-is-the-local-price-gap-that-the-grower-controls.md) — the basis rule; marketing execution depends on understanding basis.

## Provenance

Standard commodity marketing discipline codified by university extension programs (Iowa State, Purdue, University of Illinois farmdoc); the tranche approach and breakeven-first framing is the Certified Crop Adviser (CCA) grain marketing standard [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
