# Build WACC from sourced components — never type "10%" and move on

**Status:** Absolute rule
**Domain:** Valuation / discount rate
**Applies to:** `finance`

---

## Why this exists

The discount rate is the single most powerful lever in a DCF — a 100 bps move in WACC can swing enterprise value by double digits, because it compounds across every forecast year and dominates the terminal value. A WACC stated as a bare "10%" is therefore an undefended assumption sitting under the most sensitive part of the whole valuation, and it is the `valuation-analyst` agent's named anti-pattern: "WACC inputs not sourced (just '10%' with no build)." Every component — risk-free rate, equity risk premium, beta, size premium, country premium, cost of debt, capital weights — must be built up from a citable source with a date, so a reviewer (or a deposition) can challenge any one input and see exactly where it came from. WACC is also **volatile**: the risk-free rate and ERP move with markets, so a sourced WACC carries a refresh date.

## How to apply

Build cost of equity via CAPM, blend with after-tax cost of debt at target capital weights, and cite every input with its source and date:

```
Cost of equity (CAPM):
  Risk-free rate    Rf       src: 10-yr govt yield, <date>                 [volatile — refresh]
  Equity risk prem  ERP      src: Damodaran implied ERP, <month/year>      [volatile — refresh]
  Levered beta      β        src: sector beta, re-levered to target D/E    [unverified if from memory — pull fresh]
  Size premium      SP       src: published size-premium study, <year>
  Country prem      CRP      src: Damodaran country risk premium (if non-domestic)
  Ke = Rf + β·ERP + SP + CRP
Cost of debt:
  Kd_after_tax = pre-tax cost of debt × (1 − tax rate)    # cost of debt from the actual debt stack, not a guess
Weights (target, not snapshot):
  WACC = (E/V)·Ke + (D/V)·Kd_after_tax
```

**Do:**
- Cite **each** component with source + date; the risk-free rate and ERP are market-volatile — mark them and carry a refresh date (house opinion #11, models age).
- Use **target** capital weights for a going-concern valuation, not a single-day market snapshot that may be atypical.
- Re-lever beta to the subject's target capital structure rather than borrowing a comp's levered beta unadjusted.

**Don't:**
- Type a single WACC number with no build — that is the named anti-pattern.
- State a beta or ERP "from memory" as fact — pull it fresh and cite it, or mark it `[unverified — training knowledge]` and verify before it gates the valuation.
- Mix a current-snapshot risk-free with a stale ERP from a different date — date-align the components.

## Edge cases / when the rule does NOT apply

- **Regulated entities** may use a regulator-prescribed allowed return rather than a market CAPM build — use it and cite the regulatory determination, not a self-built WACC.
- **Adjusted Present Value (APV)** approaches discount unlevered cash flows at the unlevered cost of equity and value the tax shield separately — the component-sourcing discipline still applies to each piece.
- **A back-of-envelope sanity check** may use a rounded sector WACC to gut-check magnitude — but the valuation of record carries the full sourced build.

## See also

- [`./valuation-triangulate-three-methods.md`](./valuation-triangulate-three-methods.md) — WACC discounts the DCF leg of the triangulation.
- [`./valuation-discipline-the-terminal-value.md`](./valuation-discipline-the-terminal-value.md) — where a small WACC error does the most damage.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — each WACC component is a labelled, sourced input cell.
- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — "WACC components are sourced"; the unsourced-WACC anti-pattern.
- [`../skills/dcf-valuation/SKILL.md`](../skills/dcf-valuation/SKILL.md) — the WACC-build-from-primary-sources step.

## Provenance

Codifies the `valuation-analyst` agent's "WACC components are sourced" opinion and "WACC inputs not sourced" anti-pattern ([`../agents/valuation-analyst.md`](../agents/valuation-analyst.md)), house opinion #1 (source-cite every number) and #11 (models age) in [`../CLAUDE.md`](../CLAUDE.md) §3, and the `dcf-valuation` skill's WACC-from-primary-sources step (§8). New.

---

_Last reviewed: 2026-05-30 by `claude`_
