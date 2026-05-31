---
description: Build a linked, self-checking three-statement model — inputs in one sourced place, a driver-based forecast, a derived (never typed) indirect cash-flow bridge, one scenario switch, disclosed circulars, and an error-check block that returns zero.
argument-hint: "[the subject, e.g. 'a 5-year model for a mid-sized SaaS business']"
---

# Build a three-statement model

You are running `/finance:build-three-statement-model`. Build the integrated P&L / balance sheet / cash-flow model for what the user described (`$ARGUMENTS`), following this plugin's `financial-modeler` discipline. A model that balances because someone plugged a number is not a model — it is a number that is about to lie.

## When to use this

Building or rebuilding an operating / transaction model that needs all three statements to tie. Not for a standalone margin walk or single-statement quick analysis (no BS or CF to link) and not for the direct-method 13-week cash forecast (a different artifact — use the treasury cash command).

## Steps

1. **Keep every input in one labelled, sourced place** (`inputs-live-in-one-place`): promote every literal rate / growth / margin to a labelled Inputs cell with a source citation and refresh date — no `*0.21` buried in a formula. Blue = hardcoded input, black = formula, green = link; a black cell with a literal rate is a smell.
2. **Drive the forecast off operational drivers** (`model-drive-the-forecast-off-operational-drivers`): decompose each material line into quantity x rate (SaaS ARR roll, usage x price, headcount x fully-loaded cost) — not `=PriorRevenue * (1 + growth%)`. Benchmark each driver against history before locking it.
3. **Link the three statements — derive cash flow, never type it** (`link-the-three-statements`): net income flows to retained earnings and to the top of the CF; every CF line is a period-over-period change in a BS account; ending cash on the CF lands on the BS. No plug.
4. **Build the indirect cash-flow bridge in canonical order** (`model-derive-the-cash-flow-bridge-from-net-income`): operations (non-cash add-backs first, then working capital signed by direction of movement) → investing (capex ties to the PP&E roll) → financing (Δdebt ties to the debt schedule). A mis-signed working-capital line is the most common error.
5. **Drive scenarios from one switch** (`model-present-scenarios-driven-by-one-switch`): one `ScenarioSwitch` on the Inputs sheet read everywhere (base / upside / downside), never scattered `IF`s; present a range, not a single point.
6. **Disclose every circular and carry an error-check block** (`model-design-disclose-circular-references`, `model-carry-an-error-check-block`): isolate the one legitimate interest-on-cash-sweep loop behind a switch and document it; every other circular is a bug. Aggregate `BalanceCheck`, `CashTie`, RE / debt / PP&E roll ties into one master flag that reads 0 when clean.

## Guardrails

- A non-zero master error-check flag is a stop-ship signal — fix it or label the model draft/blocked; never wrap a failing tie in `IFERROR(...,0)` to make it green.
- State the basis on every revenue figure (GAAP recognized vs bookings vs billings vs ARR) — never blend GAAP and management views silently.
- Carry a `model-documentation.md` (version, assumptions, owner, last refresh); models age. Scrub confidential figures before sharing examples.
