# Procurement decision trees

Which analysis for which question — traverse top-to-bottom before picking a method.

## Decision Tree: Where can we save?

1) Build the spend cube (§3 #5). 2) Segment categories (Kraljic) (§3 #1). 3) For each: sourcing (TCO/should-cost), demand, or risk play. 4) Track to a finance baseline (§3 #3).

## Decision Tree: How should I source this?

1) Place on the Kraljic matrix (§3 #1). 2) Match the play. 3) Run on TCO, not price (§3 #2).

## Decision Tree: Are our savings real?

1) Set a finance baseline (§3 #3). 2) Measure realized vs negotiated. 3) Locate leakage and reconcile to the P&L.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Segment the spend (Kraljic)** → use when: Place a category on the supply-risk × spend matrix and match the sourcing play before sourcing, so you don't auction a strategic single-source. ([`../skills/segment-the-spend/SKILL.md`](../skills/segment-the-spend/SKILL.md))
- **Source on total cost of ownership** → use when: Run a sourcing decision on TCO — freight, quality, switching, inventory, lifecycle — not unit price, so a price 'savings' doesn't raise total cost. ([`../skills/source-on-tco/SKILL.md`](../skills/source-on-tco/SKILL.md))
- **Manage supplier risk as a portfolio** → use when: Assess supplier and concentration risk across the base and mitigate single-source exposure, instead of a one-time checkbox. ([`../skills/manage-supplier-risk/SKILL.md`](../skills/manage-supplier-risk/SKILL.md))
- **Build the spend cube** → use when: Build and classify the spend cube by category, supplier, and business unit, surfacing tail spend, so strategy rests on visibility. ([`../skills/build-the-spend-cube/SKILL.md`](../skills/build-the-spend-cube/SKILL.md))
- **Validate realized savings** → use when: Measure realized savings against a finance-recognized baseline and locate leakage, so negotiated savings aren't mistaken for P&L impact. ([`../skills/validate-realized-savings/SKILL.md`](../skills/validate-realized-savings/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`sourcing-lead`](../agents/sourcing-lead.md)
- **Sourcing** → [`category-strategist`](../agents/category-strategist.md)
- **Risk** → [`supplier-risk-specialist`](../agents/supplier-risk-specialist.md)
- **The numbers** → [`spend-analytics-analyst`](../agents/spend-analytics-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Segment the spend before you source it — if this is in question, apply §3 #1 before any method.
2. Source on total cost of ownership, not unit price — if this is in question, apply §3 #2 before any method.
3. Realized savings ≠ negotiated savings — track to the P&L — if this is in question, apply §3 #3 before any method.
4. Supplier risk is a portfolio, not a checkbox — if this is in question, apply §3 #4 before any method.
5. Spend visibility comes before strategy — if this is in question, apply §3 #5 before any method.
6. Should-cost beats benchmarking for leverage — if this is in question, apply §3 #6 before any method.
7. Demand management often beats price negotiation — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark and index — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
