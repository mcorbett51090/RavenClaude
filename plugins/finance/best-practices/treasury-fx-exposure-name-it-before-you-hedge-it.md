# Name the FX Exposure Before You Hedge It

**Status:** Absolute rule
**Domain:** Treasury / FX risk management
**Applies to:** `finance`

---

## Why this exists

FX hedging programs that don't start with an explicit exposure inventory routinely hedge the wrong thing — or hedge exposures that offset each other naturally and don't need hedging at all. A company with USD revenue and EUR costs has a structural long-USD position; adding a EUR/USD forward that buys EUR amplifies the exposure rather than reducing it. Worse, the hedge itself generates mark-to-market volatility under ASC 815 / IFRS 9 that can dwarf the original exposure. The name-it-first discipline ensures you know the sign, size, tenor, and certainty of an exposure before committing to an instrument.

## How to apply

Build an exposure inventory before selecting any hedging instrument.

```
FX Exposure Inventory — Minimum Required Fields
────────────────────────────────────────────────
Currency pair          | Direction (long/short FCY) | Notional amount | Period / tenor
Exposure type          | Transactional / Translational / Economic
Certainty              | Highly probable / Probable / Possible / Speculative
Existing natural offset| Yes (describe) / No
Hedge eligibility      | ASC 815 / IFRS 9 designation or undesignated
Current hedge in place | Instrument — notional — maturity — counterparty
Residual net exposure  | = Gross exposure - Natural offset - Hedged notional
```

**Do:**
- Quantify natural offsets first — matching EUR revenues against EUR costs before buying a hedge eliminates the need for the instrument entirely.
- State the certainty of forecasted transactions (highly probable is the ASC 815 / IFRS 9 threshold for cash-flow hedge designation).
- Document the hedge designation memo at inception if seeking hedge accounting treatment; after-the-fact designation does not qualify.
- Re-run the exposure inventory each forecast cycle, not just at hedge inception.

**Don't:**
- Enter a hedge instrument before documenting the underlying exposure it is intended to cover.
- Assume a forward that "looks right" reduces risk without checking the sign of the underlying position.
- Run undesignated hedges without understanding that fair-value changes will hit P&L each period under ASC 815 / IFRS 9.
- Let the exposure inventory go stale — a hedge that matched an exposure 6 months ago may no longer match it today.

## Edge cases / when the rule does NOT apply

- **Purely speculative FX positions** (e.g., a treasury taking a view on a currency) — not a hedging program; document as speculative and apply appropriate governance approvals.
- **De minimis exposures** below the company's stated materiality threshold — document the threshold and the decision not to hedge, but a full inventory is not required.

## See also

- [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md) — owns the FX exposure inventory and hedge program design.
- [`./treasury-cite-the-agreement-on-every-covenant.md`](./treasury-cite-the-agreement-on-every-covenant.md) — credit-facility covenants often restrict the type or notional size of permitted hedges; check before transacting.

## Provenance

Codifies the treasury-analyst's FX hedge design discipline from the finance plugin's CLAUDE.md §1 (treasury agent owns "FX exposure, banking ops"). The ASC 815 / IFRS 9 designation and certainty thresholds are domain-standard; confirm against current standard guidance for a live deliverable. Natural-offset-first discipline reflects standard corporate treasury practice.

---

_Last reviewed: 2026-06-05 by `claude`_
