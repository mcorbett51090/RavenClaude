# DSCR Must Be Modeled Through the Hold, Not Just at Close

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

A deal that clears 1.25x DSCR at origination may fall below the lender's covenant threshold in year 3 if a major tenant vacates. A DSCR calculated only at the acquisition date answers the wrong question — it tells the lender whether the loan closes, not whether the investment survives the hold. Modeling DSCR year-by-year through the projected hold, with stress scenarios tied to the lease expiration schedule, is the analysis that identifies whether the equity is at risk before the lender's call.

## How to apply

Build a DSCR timeline as part of every leveraged acquisition model:

```
DSCR Waterfall — [Property Name]
──────────────────────────────────
Loan: $______   Rate: ___% ([ ] fixed  [ ] floating)   Maturity: ____

Year  | NOI      | Annual Debt Service | DSCR   | Lender Covenant | Status
──────|----------|---------------------|--------|-----------------|────────
  1   | $        | $                   |        | ≥ ___x          |
  2   | $        | $                   |        |                 |
  3   | $        | $                   |        |                 |
  4   | $        | $                   |        |                 |
  5   | $        | $                   |        |                 |
  Refi| $        | $ (refi at ___% cap)|        |                 |

DSCR stress scenario — if [largest tenant] does not renew (Year [X]):
  Stressed NOI:          $______
  Stressed DSCR:         ___x
  DSCR covenant breach?  [ ] Yes  [ ] No

Refi coverage: Can the loan refi at maturity at a market cap rate of ___% with DSCR ≥ ___x?
  [ ] Yes  [ ] No — equity must contribute $______
```

**Do:**
- Flag any year where modeled DSCR drops within 10% of the lender's covenant threshold — that is the early-warning zone.
- Run the stress scenario where the largest single tenant vacates at their first expiration option; show the DSCR impact explicitly.
- For floating-rate loans, model DSCR across a rate range (base, +100 bps, +200 bps) — interest-rate risk is inseparable from coverage risk on floating debt.

**Don't:**
- Present only the going-in DSCR at origination; the IC needs the hold-period timeline.
- Conflate DSCR with LTV — they measure different risks; a deal can have low LTV and still have a DSCR problem if NOI is thin relative to the debt service.
- Assume NOI growth covers DSCR erosion without showing the math; NOI growth assumptions require a sourced basis.

## Edge cases / when the rule does NOT apply

All-cash acquisitions have no debt service obligation and no DSCR to model; substitute a return-on-cost and unlevered IRR as the coverage metrics.

## See also

- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — owns the DSCR model and hold-period debt stress.
- [`./debt-is-the-swing-factor-not-the-cap-rate.md`](./debt-is-the-swing-factor-not-the-cap-rate.md) — the governing rule on modeling debt as the primary hold-period risk factor.

## Provenance

Codifies CLAUDE.md §3 #6 (debt is the swing factor, not the cap rate) with a specific hold-period DSCR instrument. Annual DSCR modeling through the hold is standard institutional underwriting practice and a common lender requirement for stabilized acquisition financing [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
