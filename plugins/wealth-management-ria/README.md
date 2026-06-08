# Wealth Management (RIA)

The **wealth-management-ria** plugin — the personal financial-advisory craft of a Registered Investment Adviser serving individual clients: goal-based planning, portfolio construction with a written Investment Policy Statement, and the fiduciary/compliance + client-review oversight that makes the practice defensible. Distinct from corporate finance (FP&A / treasury — that's `finance`).

> **Not investment advice.** Everything this plugin produces is educational and operational support for an advisory practice — **not** personalized investment, tax, or legal advice and **not** a recommendation to buy or sell any security. A licensed human adviser applies the frameworks to a specific client after confirming suitability; a CPA / attorney owns the tax and legal conclusions.

## Agents

- **`financial-planner`** — Goal-based planning: turning life goals into a cash-flow and savings plan, the retirement & withdrawal strategy (the 4% rule, dynamic guardrails, sequence-of-returns risk), tax-aware planning across account types (Traditional/Roth IRA, 401(k), taxable, HSA — the funding order, the Roth question), and estate basics (beneficiaries, titling, the documents to have). Builds the plan the IPS later implements.
- **`portfolio-analyst`** — Portfolio construction: target asset allocation & diversification, the Investment Policy Statement (objectives, constraints, ranges, rebalancing rules), rebalancing strategy (calendar vs threshold/bands), risk & factor basics, and tax-efficient implementation (asset location, tax-loss harvesting + the wash-sale rule).
- **`advisory-compliance-and-client-review-lead`** — Advisory oversight: fiduciary duty (Advisers Act) vs Reg BI, Form ADV basics (Parts 1 / 2A / 2B / CRS), suitability/KYC, periodic client reviews (cadence + agenda), books-and-records, and marketing-rule basics. The gate that makes the plan and the IPS defensible.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install wealth-management-ria@ravenclaude
```

## Seams

- **Corporate finance — FP&A, treasury, company forecasting** → `finance`; this plugin is *personal* financial advisory ("model the household's retirement cash flow"), not corporate ("model the company's cash flow").
- **Deep, multi-jurisdiction securities-law interpretation, registration mechanics, enforcement** → `regulatory-compliance`; this plugin covers fiduciary / Reg BI / Form ADV *basics*.
- **The billing/payment system that charges the advisory fee** → `fintech-payments-engineering`; this plugin designs the practice, not the payment rails.
- **Client PII handling, data security, access controls** → `ravenclaude-core/security-reviewer`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Pairs with `finance`, `regulatory-compliance`, and `fintech-payments-engineering`.
