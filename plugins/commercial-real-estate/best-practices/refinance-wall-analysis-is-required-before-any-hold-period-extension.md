# Refinance Wall Analysis Is Required Before Any Hold-Period Extension

**Status:** Absolute rule
**Domain:** Commercial real estate / debt management
**Applies to:** `commercial-real-estate`

---

## Why this exists

The "refinance wall" — the period when a significant share of commercial real estate debt matures simultaneously in a rising-rate environment — was the dominant deal-killer of 2023–2025. Owners who extended hold periods expecting rates to fall instead faced loan maturities they could not refinance at their original underwriting assumptions. The structural risk is this: a 3- or 5-year interest-only loan originated at a 3.5% rate with a 65% LTV is not refinanceable at maturity in a 6.5% rate environment at the same LTV without either paying down substantial principal or accepting DSCR coverage that trips lender covenants. Before extending any hold period, the refinance scenario at current rates and realistic NOI must be stress-tested — not assumed to be manageable.

## How to apply

Run the refinance wall analysis at three rate scenarios before any hold-period decision:

```
Refinance Wall Analysis — [Asset] [Date]
─────────────────────────────────────────
Current loan:
  Loan balance at maturity:        $___
  Maturity date:                   [Date]
  Current LTV:                     ___%
  In-place NOI at maturity (est.): $___

Refinance scenario at maturity:
  Scenario          │  Rate (%)  │  LTV   │  Loan proceeds  │  DSCR   │  Equity gap ($)
  ──────────────────┼────────────┼────────┼─────────────────┼─────────┼────────────────
  Bull (rate -100bp)│            │        │                 │         │
  Base (rate flat)  │            │        │                 │         │
  Bear (rate +100bp)│            │        │                 │         │

DSCR minimum required by lender assumption: 1.25×

Equity gap = max(0, existing loan balance - refinance proceeds)
  If equity gap > 0 → must pay down or inject equity at maturity
  Bear-case equity gap: $___

  At what NOI does the loan break even on refinance at current rates?
  Break-even NOI: $___ = required debt service ÷ min DSCR × loan proceeds at LTV cap
```

**Decision matrix:**

| Bear-case equity gap | Remaining hold period | Recommended action |
|---|---|---|
| < 5% of asset value | > 24 months | Hold — manageable risk |
| 5–15% of asset value | 12–24 months | Plan equity injection or sell before maturity |
| > 15% of asset value | < 12 months | Sell, sell with leaseback, or negotiate extension now |
| Any | < 6 months | Immediate lender engagement — do not wait |

**Do:**
- Run this analysis at acquisition, at every annual asset review, and at any hold-period extension decision — market rates move and the refinance exposure changes.
- Present the bear-case equity gap to the IC alongside the IRR sensitivity; a deal with a 15% IRR at base rates and a $5M equity gap in the bear case is a different risk than a 12% IRR with no gap.
- Engage the lender at least 180 days before maturity — lenders negotiate extension terms for well-performing assets; they foreclose on surprises.
- Model the DSCR at the bear-case rate against the lender's covenant threshold explicitly — a DSCR of 1.26× at base that drops to 0.98× in the bear case is a covenant trip, not just a financial inconvenience.

**Don't:**
- Assume rates will normalize before the loan matures without a specific dated source — "rates will come down" is not an underwriting assumption, it is a guess.
- Run the refinance model at the original LTV without checking whether the market cap rate has moved — a rising cap rate compresses value and constrains refinance proceeds independent of the interest rate.
- Conflate "the loan isn't due yet" with "the refinance risk isn't present yet" — a 24-month runway is the time to act, not the time to wait.

## Edge cases / when the rule does NOT apply

Free-and-clear assets (no debt) do not have a refinance wall — the equivalent risk for an unleveraged hold is a forced-sale scenario when the hold period extends into a down market. Fixed-rate long-term debt (10-year CMBS, agency debt) with a maturity well beyond the expected hold period has minimal refinance-wall exposure during the hold; the rule applies at loan maturity planning, not ongoing.

## See also
- [`../agents/acquisitions-underwriter.md`](../agents/acquisitions-underwriter.md) — models debt sizing, DSCR path, and the refinance wall at acquisition.
- [`../agents/asset-property-manager.md`](../agents/asset-property-manager.md) — owns the hold-period asset plan and NOI growth that feeds the refinance scenario.
- [`../knowledge/cre-underwriting-economics.md`](../knowledge/cre-underwriting-economics.md) — covers DSCR, LTV, and debt-sizing mechanics.

## Provenance

Codifies the refinance-wall discipline that emerged from the 2023–2025 CRE distress cycle; consistent with CBRE Research and MSCI/RCA debt maturity analysis methodology [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
