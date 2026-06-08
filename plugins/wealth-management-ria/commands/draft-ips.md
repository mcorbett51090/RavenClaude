---
description: "Draft an Investment Policy Statement and target allocation as education: objectives, constraints, ranges, a rebalancing rule, and tax-aware implementation — not personalized advice."
argument-hint: "[plan + risk profile + account types + tax situation]"
---

You are running `/wealth-management-ria:draft-ips`. Use `portfolio-analyst` + the `portfolio-construction-and-ips` skill.

## Steps
1. Draft the IPS scaffold: objectives, constraints (liquidity, horizon, taxes, legal, unique), target allocation with ranges, rebalancing rule, review triggers, monitoring.
2. Set the target asset allocation for the stated risk profile and horizon — always with ranges; a target with no band is unenforceable.
3. Choose and document the rebalancing rule (calendar vs threshold/bands) with the trading-cost / drift / tax trade-offs; prefer bands in taxable accounts with a max-time backstop.
4. Design tax-aware implementation: asset location across taxable/tax-deferred/tax-free, tax-loss harvesting + the wash-sale rule; route bracket specifics to a CPA.
5. Route next steps: the underlying plan → `financial-planner`; suitability + recording the IPS in books-and-records → `advisory-compliance-and-client-review-lead`.
6. Emit the draft IPS + the Structured Output block, with the `Not investment advice:` and `Client-specific facts to confirm:` lines.
