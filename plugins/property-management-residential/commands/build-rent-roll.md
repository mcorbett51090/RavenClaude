---
description: "Build the residential rent roll, a delinquency summary with a consistent collections ladder, and an owner statement with operating-only NOI and occupancy/vacancy — handing the books of record to finance."
argument-hint: "[the portfolio/property + available data (units, rents, balances, expenses)]"
---

You are running `/property-management-residential:build-rent-roll`. Use `owner-and-portfolio-reporting-analyst` + the `owner-reporting-and-rent-roll` skill.

## Steps
1. Build the rent roll (unit, tenant, lease term, market vs. actual rent, balance/aging, status) reconciled to reality — flag any balance that doesn't reconcile as a data-integrity problem to fix first.
2. Summarize delinquency (aging, concentration) and define ONE documented collections ladder applied to every account; flag selective enforcement and route legal steps to counsel.
3. Compute NOI as operating income − operating expenses, EXCLUDING debt service, capex, and depreciation; never call it cash flow. Say which question you're answering.
4. Produce the owner statement (income, opex, distributions, NOI, occupancy/vacancy) and route the books of record — trust-account reconciliation, GL, tax — to finance.
5. Keep tenant PII out of the output. Emit the rent roll / statement + the Structured Output block (with `Fair-housing / habitability flags:` and `Handoff:`).
