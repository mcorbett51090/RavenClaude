---
name: owner-reporting-and-rent-roll
description: "Build the residential rent roll as the source of truth, analyze delinquency and run a consistent documented collections ladder, produce the owner statement, compute operating-only NOI (excluding debt service, capex, depreciation — never cash flow), and report occupancy/vacancy — handing the books of record to finance."
---

# Owner Reporting & Rent Roll

## The rent roll is the source of truth or it's nothing
The system-neutral schema — unit, tenant, lease start/end, market vs. actual rent, balance/aging, status (occupied / vacant / notice / down) — reconciles to reality every period. A drifted rent roll mis-states delinquency, occupancy, and NOI at once. A balance that doesn't reconcile to the ledger is a data-integrity problem before it's a collections problem; fix the rent roll first.

## Delinquency & the collections ladder
Analyze aging and concentration (by unit, by property), then run **one** documented collections ladder — reminder → late notice → pay-or-quit → counsel — applied to every account. Selective enforcement ("let the good tenant slide") is both a fair-housing exposure and a financial-control gap. The legal steps are flagged to counsel, not executed as settled law.

## NOI is operating only
NOI = operating income − operating expenses, **excluding** debt service, capex, and depreciation. It is **not** cash flow — a statement that mixes in debt service answers the levered-cash-flow question instead; say which question you're answering. Capex (a roof, a renovation-grade turn) stays out of NOI.

## Owner statement & occupancy
The owner statement reports operations — income, operating expenses, distributions, operating-only NOI, occupancy/vacancy (physical vs. economic), vacancy loss, renewal rate, time-to-lease. The books of record — trust-account reconciliation, GL posting, audited financials, tax — belong to `finance`. Tenant PII (SSNs, bank data, screening reports) never appears in a report.

## Output
A reconciled rent roll, a delinquency analysis with a consistent collections ladder, or an owner statement with operating-only NOI and occupancy/vacancy — with the explicit seam to `finance` for the books of record. Selective enforcement is flagged; legal collections steps route to counsel.
