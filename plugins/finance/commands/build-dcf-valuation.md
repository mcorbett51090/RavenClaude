---
description: Build a defensible DCF and triangulate it — WACC built from sourced, dated components; terminal value capped at long-run GDP and computed both ways then reconciled; a WACC x terminal-growth sensitivity; and three weighted methods presented as a range, never a single point.
argument-hint: "[the target, e.g. 'a DCF for a mid-sized acquisition target']"
---

# Build a DCF valuation

You are running `/finance:build-dcf-valuation`. Value the business the user described (`$ARGUMENTS`), following this plugin's `valuation-analyst` discipline. A valuation on one method is an estimate; a single-point answer hides the judgment behind it.

## When to use this

A pre-investment / pre-acquisition valuation, a 409A refresh, board-discussion prep, or fairness-opinion support. Not for a pre-revenue company where a DCF cannot be calibrated (substitute VC method / scorecard for the DCF leg, but still triangulate).

## Steps

1. **Sit the DCF on a linked model** (`link-the-three-statements`): the free-cash-flow forecast comes off a three-statement model that ties, with inputs in one sourced place — a DCF on an unbalanced model inherits the model's lie.
2. **Build WACC from sourced, dated components** (`valuation-build-wacc-from-sourced-components`): cost of equity via CAPM (risk-free, ERP, re-levered beta, size/country premia — each cited with source + date), blended with after-tax cost of debt at target capital weights. Never type a bare "10%"; mark the market-volatile inputs (Rf, ERP) and carry a refresh date.
3. **Discipline the terminal value** (`valuation-discipline-the-terminal-value`): cap perpetual growth at long-run nominal GDP; compute TV both ways (Gordon growth + exit multiple) and reconcile — the implied exit multiple from Gordon should be consistent with the comp set. Disclose the share of EV that is terminal (flag if > ~75%).
4. **Run the WACC x terminal-growth sensitivity** (`model-present-scenarios-driven-by-one-switch`): these two move the answer most; build the grid and present a range, not a point.
5. **Triangulate three weighted methods** (`valuation-triangulate-three-methods`): DCF + trading comps + precedent transactions, each with an explicit weight and a one-line rationale, presented as a football field — range first, midpoint second. When methods diverge materially, name *why* in the narrative; the divergence is signal.

## Guardrails

- Don't state a beta or ERP from memory as fact — pull it fresh and cite it, or mark it `[unverified - training knowledge]` and verify before it gates the valuation.
- Never present a single-point valuation as "the answer," and never use `(DCF + comps) / 2` with no stated weights.
- Document the comp set: why each comp is in, why each near-miss is out (stage / geography / model / margin profile). Verifying current comparable financials or accounting-standard specifics routes to `ravenclaude-core/deep-researcher`.
