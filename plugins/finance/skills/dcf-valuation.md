---
name: dcf-valuation
description: Run a defensible discounted-cash-flow valuation — explicit projection period, terminal value (Gordon vs exit-multiple), WACC build, sensitivities, scenario weighting, and the cross-check against trading / precedent multiples. Reach for this skill on any valuation work (pre-investment, 409A, fairness opinion, M&A) where a number has to survive board / counterparty scrutiny. Used by `valuation-analyst` (primary) and `financial-modeler`.
---

# Skill: dcf-valuation

**Purpose:** Build a DCF that holds up under cross-examination. The mechanics are simple; the defensibility lives in the assumption set and the cross-checks. Used by `valuation-analyst` (primary).

## When to use

- Pre-investment / pre-acquisition valuation
- 409A refresh
- Fairness-opinion support
- Strategic value-creation modeling (board / LP discussion)
- M&A diligence (buy-side or sell-side)
- Impairment testing (goodwill, indefinite-lived intangibles)

## The pieces

A DCF has four parts. Each requires defensible inputs:

1. **Explicit projection period** — typically 5-10 years, ending when the business is at steady-state
2. **Terminal value** — Gordon growth OR exit multiple (do both, compare, explain)
3. **Discount rate (WACC)** — build from comparable-set betas, current risk-free, ERP, size premium, company-specific premium
4. **Enterprise → equity bridge** — net debt, minority interest, preferred, options dilution

## Explicit projection period

**Length:** long enough that the terminal year reflects steady-state. Most growth-stage businesses need 7-10 years. Mature businesses can use 5. Avoid 3-year DCFs — terminal value dominates and the model is a single-line bet on the multiple.

**Steady-state criteria** (terminal year should satisfy):

- Revenue growth has converged to a sustainable long-run rate (typically 2-3% real; can be higher for genuinely durable platforms)
- Margins have stabilized (not still climbing the curve)
- Reinvestment rate (capex + ΔNWC / revenue) is consistent with the long-run growth rate
- Tax rate is at expected long-run effective rate

If the year-N → year-N+1 trajectory still shows margin expansion or growth deceleration, extend the projection. Forcing terminal value on a non-steady-state year overstates value.

**Use the [`./driver-based-forecasting.md`](./driver-based-forecasting.md) skill to build the projection.** A DCF on a top-down "grow 15% a year" forecast is just a calculator.

## Terminal value: do both methods

### Gordon growth (perpetuity)

```
TV = FCF_(N+1) / (WACC - g)
```

Where:
- `FCF_(N+1)` = next year's free cash flow (NOT the terminal year — one year forward)
- `g` = long-run nominal growth rate (typically 2-3%, capped at long-run GDP nominal)

**Smell test:** terminal value > 75% of enterprise value usually means either projection too short OR g too high.

### Exit multiple

```
TV = Terminal-year EBITDA × Exit multiple
```

Where the exit multiple comes from the comparable-set trading multiples at the implied terminal-year size / growth / margin profile — NOT today's multiple applied forward.

**Reconciliation:** implied perpetuity-growth from the exit multiple should be defensible. Solve:

```
g_implied = WACC - (FCF_(N+1) / TV_(exit multiple))
```

If `g_implied > 4%`, the exit multiple is generous for the terminal-year profile. Adjust one of the inputs.

**Always present both.** A DCF that uses only Gordon undersells the M&A reality; one that uses only exit multiples can't defend against rate-environment shifts.

## WACC

Build from primary inputs, not "industry WACC = 9%."

```
WACC = (E/V) × Re + (D/V) × Rd × (1 - t)
```

### Cost of equity (Re)

```
Re = Rf + β_levered × ERP + size_premium + alpha
```

Where:
- **Rf** — risk-free rate. Match the projection currency and duration. 10Y Treasury yield for USD; sovereign-curve equivalent in other currencies. Use the spot or a recent average (avoid cherry-picking a single date).
- **β_levered** — re-lever the comparable-set's unlevered beta at the subject company's target capital structure.

  ```
  β_unlevered = β_levered_peer / [1 + (1-t) × (D/E)_peer]
  β_levered_target = β_unlevered_peer_avg × [1 + (1-t) × (D/E)_target]
  ```

- **ERP** — equity risk premium. Use a recent published estimate (Damodaran's annual; the practitioner's go-to). State the source and the date.
- **Size premium** — for sub-large-cap targets. Source from Duff & Phelps / Kroll annually-updated tables (or equivalent). Don't double-count with alpha.
- **Alpha (company-specific premium)** — used sparingly for genuinely unique risk that isn't in the comparable beta. State explicitly and defend.

### Cost of debt (Rd)

The marginal rate the company would borrow at today, not the historical-coupon rate on existing debt. Use the comparable-set's debt cost or a synthetic rating-based estimate.

### Tax rate

Use the long-run effective tax rate the company expects to pay — typically near the statutory federal + state blended rate. NOL carryforwards affect the projection cash flows directly, NOT the WACC.

### Capital structure weights

Target capital structure, not snapshot. A company with zero debt today but plans to lever 40% next year uses target weights.

**WACC sensitivity is the single biggest swing factor.** Always show a sensitivity table for WACC × terminal growth or WACC × exit multiple.

## Free cash flow construction

**Unlevered free cash flow** (the right metric for enterprise DCF):

```
EBIT
× (1 - tax rate)               → NOPAT
+ Depreciation & Amortization
- Capex
- Δ Net Working Capital
+ Stock-based-comp adjustment (if treating as non-cash; controversial — see note)
= Unlevered FCF
```

**Stock-based comp note:** treating SBC as non-cash overstates value. Best practice in 2026 — treat SBC as a real cost. Either (a) leave it in EBIT (preferred), or (b) add it back but offset with dilution-equivalent share issuance in the bridge.

## Discounting convention

Two valid approaches; pick one and apply consistently:

- **End-of-period** — `discount factor = 1 / (1+WACC)^N`. Conservative, common for closely-held businesses.
- **Mid-period** — `discount factor = 1 / (1+WACC)^(N - 0.5)`. Assumes cash flows are received evenly through the year. Common for public-company DCFs.

Mid-period adds ~half a year of value vs. end-of-period. State which convention you used.

## Enterprise → equity bridge

```
Enterprise Value (= Σ discounted FCF + discounted TV)
- Total debt (book or market — usually book is close enough)
- Preferred stock
- Minority interest
- Underfunded pension liability (if material)
+ Cash & cash equivalents (excluding restricted)
+ Net non-operating assets
= Equity value
÷ Diluted shares outstanding (treasury-stock-method or fully-diluted; state which)
= Implied price per share
```

**Diluted shares:** for options / RSUs / warrants, use treasury-stock method if strike < current price; otherwise exclude. For convertible securities, use if-converted method when in-the-money. State the method and the strike-distribution.

## Sensitivity tables

Mandatory output for any DCF. Two-variable sensitivity on at least:

- Enterprise value vs. (WACC, terminal growth)
- Enterprise value vs. (WACC, exit multiple)
- Equity value per share vs. (WACC, revenue CAGR)
- Equity value per share vs. (EBITDA margin in terminal year, terminal growth)

Color-code so the central estimate is visible and the corners of the table show the realistic range, not a 10× swing.

## Cross-check: trading comps + precedents

A DCF in isolation is hubris. Cross-check against:

- **Trading multiples** — current EV / Revenue, EV / EBITDA, P/E for a curated comparable set of public companies. Apply to the subject's LTM and forward metrics.
- **Precedent transactions** — completed M&A deals in the same vertical at similar scale, with dates and conditions noted. Adjust for cycle (rate environment, multiple compression / expansion since deal).

Present DCF, trading comps, and precedents on a single chart — usually a football field showing the range from each method. Implied DCF value should sit somewhere in the overlap. If DCF is far outside the comp ranges, something in the DCF needs defending or revising.

## Scenarios

Run base, upside, downside on the **projection drivers**, not on WACC. Weight (e.g., 60 / 25 / 15). Weighted average is the headline; show the range too.

WACC should be the same across scenarios (it reflects discount risk for the asset class, not the operating scenario).

## Common failure modes

- **Terminal-value dominance** — TV > 80% of EV. Either projection too short or assumptions too aggressive. Extend the projection or adjust.
- **Comparable-set cherry-picking** — beta and exit multiple drawn from too few comparables, or comparables that don't actually match the business. State the inclusion criteria explicitly.
- **Stale WACC inputs** — risk-free rate from a year ago, ERP from a stale source. WACC inputs go stale within months. Date everything.
- **Optimistic terminal year** — terminal year shows margin still expanding. Force steady-state; extend the projection if you can't get there.
- **Plug** — when implied per-share value doesn't match a target, an input gets "adjusted." Don't. The DCF is the input to the conclusion, not the other way around.
- **No probability weighting** — single-scenario DCF reported as THE valuation. Always run scenarios.
- **No comp cross-check** — DCF in isolation. Always footed against trading and precedent.
- **Mixing nominal and real** — terminal growth in real terms but discount rate in nominal. Pick one and apply throughout.
- **Currency mismatch** — projection in subject's functional currency but WACC built off USD risk-free. Match currency throughout.

## Defensibility checklist

Before presenting:

- [ ] Every WACC input has a source and date (Rf, ERP, betas, size premium)
- [ ] Comparable set documented (inclusion criteria, count, key stats)
- [ ] Projection period long enough for steady-state in terminal year
- [ ] Terminal value calculated both ways (Gordon + Exit multiple) and reconciled
- [ ] Sensitivity tables on WACC × terminal growth AND WACC × exit multiple
- [ ] Football field comparing DCF to trading + precedent ranges
- [ ] Scenarios with probability weights
- [ ] BS and CF for the projection internally consistent (the underlying model passes the [`./model-review.md`](./model-review.md) 7-pass)
- [ ] Discounting convention stated (mid-year vs end-of-year)
- [ ] Stock-based-comp treatment stated and defended
- [ ] Dilution method stated (treasury stock vs fully-diluted)
- [ ] Sources cited for every load-bearing assumption

## See also

- Skill: [`./model-review.md`](./model-review.md) — 7-pass model integrity check (DCF inherits this)
- Skill: [`./driver-based-forecasting.md`](./driver-based-forecasting.md) — the projection the DCF runs on
- Skill: [`./board-pack-composition.md`](./board-pack-composition.md) — for presenting valuation work to a board
- Template: [`../templates/model-documentation.md`](../templates/model-documentation.md)
- Agent: [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md)
- Agent: [`../agents/financial-modeler.md`](../agents/financial-modeler.md)
