---
description: "Diagnose a brick-and-mortar store P&L and build a schedule-to-traffic labor plan: walk sales to four-wall contribution, find the line that moved, fix labor against traffic, and diagnose shrink."
argument-hint: "[store P&L lines + traffic/POS data + the symptom (labor % / shrink / margin)]"
---

You are running `/retail-store-operations:store-pnl-review`. Use `store-operations-lead` + the `store-labor-and-pnl` skill.

## Steps
1. Walk the store P&L: sales → gross margin → labor % → controllable expense → four-wall contribution. Name the line that moved and size the dollar gap. If the data isn't there, state the proxy used.
2. Build the labor model against the conversion-weighted traffic curve — the over-staffed dead hours, the under-staffed peak, the labor-% impact. Name which you're trading (labor % vs. conversion).
3. If shrink is in scope, diagnose it: split operational vs. theft vs. vendor/admin, name the likely driver, prescribe the cheapest counter-measure per bucket. Route surveillance / employee-PII to `ravenclaude-core/security-reviewer`.
4. Tighten the relevant SOP (opening/closing/receiving/cash) — owner + the failure mode each step prevents.
5. Route the seams: online channel → `ecommerce-dtc`; dashboard/warehouse → `data-platform`.
6. Emit the store-P&L-and-labor plan + the Structured Output block (with `P&L impact:` and `Handoff to neighbours:`).
