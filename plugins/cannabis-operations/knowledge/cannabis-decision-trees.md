# Cannabis operations decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Licensed but losing money

1) Frame 280E COGS allocation (§3 #2). 2) Read category margin/basket (§3 #4). 3) Read inventory turns (§3 #5). 4) Check traceability cost/risk (§3 #1).

## Decision Tree: Track-and-trace doesn't reconcile

1) Pull physical vs system (§3 #1). 2) Locate the discrepancy. 3) Apply the state's corrective steps (§3 #3).

## Decision Tree: Is a rule X true here?

1) Pin the state and date (§3 #3). 2) Map the requirement. 3) Cite the regulator source (§3 #8).

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Reconcile seed-to-sale** → use when: Reconcile physical inventory to the state track-and-trace system and resolve discrepancies as compliance events, not bookkeeping. ([`../skills/reconcile-seed-to-sale/SKILL.md`](../skills/reconcile-seed-to-sale/SKILL.md))
- **Frame 280E COGS allocation** → use when: Build a defensible COGS-allocation framework under 280E, as decision-support for the CPA, so only properly-capitalized cost reduces taxable income. ([`../skills/frame-280e-cogs/SKILL.md`](../skills/frame-280e-cogs/SKILL.md))
- **Run dispensary retail on margin** → use when: Read category margin, basket, and turns and lift store profit without discount-driven traffic. ([`../skills/run-dispensary-retail/SKILL.md`](../skills/run-dispensary-retail/SKILL.md))
- **Manage the state patchwork** → use when: Anchor every compliance answer to the specific state and date, since track-and-trace, testing, potency, and tax all vary. ([`../skills/manage-the-state-patchwork/SKILL.md`](../skills/manage-the-state-patchwork/SKILL.md))
- **Read inventory turns** → use when: Read inventory turns as both a cash and a compliance metric, flagging aged and perishable product. ([`../skills/read-inventory-turns/SKILL.md`](../skills/read-inventory-turns/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`cannabis-engagement-lead`](../agents/cannabis-engagement-lead.md)
- **Traceability** → [`seed-to-sale-compliance-specialist`](../agents/seed-to-sale-compliance-specialist.md)
- **The store** → [`dispensary-retail-operations-specialist`](../agents/dispensary-retail-operations-specialist.md)
- **The numbers** → [`cannabis-finance-analyst`](../agents/cannabis-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Seed-to-sale traceability is the license — reconcile it daily — if this is in question, apply §3 #1 before any method.
2. 280E makes COGS allocation existential, not academic — if this is in question, apply §3 #2 before any method.
3. The rules change at the state line — never generalize a state — if this is in question, apply §3 #3 before any method.
4. Dispensary retail runs on margin and basket, not just traffic — if this is in question, apply §3 #4 before any method.
5. Inventory turns are a compliance AND a cash metric — if this is in question, apply §3 #5 before any method.
6. Testing and remediation are a yield-and-cost reality — if this is in question, apply §3 #6 before any method.
7. Cash and banking constraints shape operations — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every market and rule — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
