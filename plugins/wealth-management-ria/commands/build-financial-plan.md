---
description: "Build a goal-based financial plan as education: quantify goals, surface assumptions, set the funding order, and choose a retirement/withdrawal strategy — not personalized advice."
argument-hint: "[client goals + horizon + cash-flow snapshot + risk profile]"
---

You are running `/wealth-management-ria:build-financial-plan`. Use `financial-planner` + the `goal-based-financial-plan` skill.

## Steps
1. Quantify the goals: each goal gets a horizon, a funding target, and the savings it requires. Lead with goals, never a product.
2. Surface every assumption (inflation, return, longevity, horizon, savings rate) as a named, editable list; present a scenario range, not a point.
3. Set the cash-flow and account-funding order (match → high-interest debt → emergency fund → HSA if eligible → tax-advantaged → taxable); flag the eligibility/bracket facts to confirm with a CPA.
4. Choose a retirement/withdrawal strategy (4% rule vs guardrails vs cash buffer); name sequence-of-returns and longevity risk; pair the rate with a review trigger.
5. Flag estate basics (beneficiaries, titling, will/trust) and route drafting to an attorney.
6. Route next steps: allocation + IPS → `portfolio-analyst`; suitability/KYC → `advisory-compliance-and-client-review-lead`.
7. Emit the goal-based plan + the Structured Output block, with the `Not investment advice:` and `Client-specific facts to confirm:` lines.
