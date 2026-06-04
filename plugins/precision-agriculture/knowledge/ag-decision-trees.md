# Precision-ag decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Margin per acre is shrinking

1) Build per-acre economics by field (§3 #4). 2) Read yield by zone (§3 #2). 3) Optimize input economics (§3 #1). 4) Check operation timing (§3 #3).

## Decision Tree: Should I apply this input?

1) Build the response curve (§3 #1). 2) Find the economic optimum. 3) Vary by zone (§3 #2).

## Decision Tree: Sell now or store?

1) Read price, basis, and storage cost (§3 #7). 2) Weigh against risk tolerance. 3) Date the figures (§3 #8).

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Optimize input economics** → use when: Set input rates at the economic optimum where marginal return equals marginal cost, not at agronomic maximum, so the last unit pays. ([`../skills/optimize-input-economics/SKILL.md`](../skills/optimize-input-economics/SKILL.md))
- **Manage by zone** → use when: Read yield and soil by management zone and apply variable-rate inputs where they pay, instead of a field average. ([`../skills/manage-by-zone/SKILL.md`](../skills/manage-by-zone/SKILL.md))
- **Time the operations** → use when: Time planting, application, and harvest to the agronomic and weather window, since timing drives yield and quality more than rate. ([`../skills/time-the-operations/SKILL.md`](../skills/time-the-operations/SKILL.md))
- **Build fertility from data** → use when: Build the fertility program from current soil/tissue data and removal rates, not last year's program, so neither over- nor under-application costs margin. ([`../skills/build-fertility-from-data/SKILL.md`](../skills/build-fertility-from-data/SKILL.md))
- **Build per-acre economics** → use when: Build cost and margin per acre by field so the money-losing acres are visible. ([`../skills/build-per-acre-economics/SKILL.md`](../skills/build-per-acre-economics/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`agronomy-engagement-lead`](../agents/agronomy-engagement-lead.md)
- **Agronomy** → [`crop-agronomist`](../agents/crop-agronomist.md)
- **The numbers** → [`farm-operations-analyst`](../agents/farm-operations-analyst.md)
- **The outside view** → [`ag-market-analyst`](../agents/ag-market-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Manage to economic optimum, not maximum yield — if this is in question, apply §3 #1 before any method.
2. Read yield by management zone, not field average — if this is in question, apply §3 #2 before any method.
3. Time operations to the agronomic and weather window — if this is in question, apply §3 #3 before any method.
4. Cost and margin are per acre, by field — never whole-farm only — if this is in question, apply §3 #4 before any method.
5. Soil test and tissue data drive fertility, not the rear-view — if this is in question, apply §3 #5 before any method.
6. Crop protection is threshold-and-resistance management, not calendar spraying — if this is in question, apply §3 #6 before any method.
7. Weather and price are the risk — hedge the controllable, plan the rest — if this is in question, apply §3 #7 before any method.
8. Date and source any price, rate, or benchmark figure — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
