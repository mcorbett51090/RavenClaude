# Exit Cap Rate Must Be Sensitized, Not Assumed Flat

**Status:** Absolute rule
**Domain:** Commercial real estate
**Applies to:** `commercial-real-estate`

---

## Why this exists

The exit cap rate is the most consequential and least certain variable in a levered IRR model. A 50-basis-point expansion in the exit cap — entirely plausible over a 5-year hold — can reduce the levered IRR by 200–400 basis points depending on leverage and growth assumptions. A model that uses a single point estimate for the exit cap rate and presents a single IRR number to the IC is not underwriting; it is storytelling. Sensitivity tables around the exit cap are the minimum defensible standard for a CRE investment memo.

## How to apply

Every underwriting model must include an exit-cap sensitivity table as a required output:

```
Exit Cap Rate Sensitivity — Levered IRR (%)
────────────────────────────────────────────
                        Exit NOI Growth Scenario
Exit Cap Rate    | Base (0%) | Upside (+10%) | Downside (-10%)
─────────────────|-----------|---------------|─────────────────
  4.50%          |           |               |
  5.00%          |           |               |
  5.25% (base)   |  [BASE]   |               |
  5.50%          |           |               |
  6.00%          |           |               |
  6.50%          |           |               |

Notes:
  Entry cap rate:   ___%   Entry NOI: $______
  Hold period:      ___ years
  Exit cap rate assumption basis:  [going-in cap + X bps expansion / market comp / submarket trend]
  Exit cap rate source + date:     [source] — [date]

IC read:  The IRR is below [hurdle]% if exit cap expands to ___%
          The model is most sensitive to: [ ] Exit cap  [ ] NOI growth  [ ] Debt terms
```

**Do:**
- Run the sensitivity table with at minimum a ±100 bps exit-cap range from the base assumption, in 25–50 bps increments.
- State the basis for the base exit cap assumption with a source and date — "going-in cap plus 50 bps expansion" is a method, not an assumption; the entry cap + the comp set + the submarket trend is the assumption.
- Identify the break-even exit cap (the rate at which levered IRR falls below the hurdle) and present it explicitly in the IC memo.

**Don't:**
- Use the same exit cap as the going-in cap without justification — cap rate compression during a hold is a specific assumption that requires a sourced basis.
- Present only the base-case IRR without the sensitivity table — the IC needs to know the downside range, not just the expected outcome.
- Blend exit caps across a multi-asset portfolio without showing the asset-level sensitivity; blending obscures which asset carries the exit-cap risk.

## Edge cases / when the rule does NOT apply

Short-term value-add plays with a 12–24 month hold may use a market-sale pricing comp approach rather than a cap-rate exit model. In those cases, the sensitivity is on price-per-sf or price-per-unit, not a cap rate, and the same range-of-outcomes discipline applies.

## See also

- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — owns the exit-cap sensitivity model and presents it to the IC.
- [`./debt-is-the-swing-factor-not-the-cap-rate.md`](./debt-is-the-swing-factor-not-the-cap-rate.md) — the companion rule on debt sensitivity as the co-equal swing factor.

## Provenance

Codifies CLAUDE.md §3 #2 (cap rate and discount rate are not interchangeable) and the standard institutional-grade underwriting requirement for sensitivity analysis. Exit-cap sensitivity is required in virtually every institutional acquisition template (NCREIF, ULI, real estate PE firm standards) [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
