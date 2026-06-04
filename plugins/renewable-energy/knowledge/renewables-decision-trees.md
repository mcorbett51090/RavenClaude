# Renewables decision trees

Which analysis for which question — traverse top-to-bottom before picking a method.

## Decision Tree: Does this project pencil?

1) Model LCOE and IRR on net cost (§3 #1, #4). 2) Size on P90 (§3 #6). 3) Model the interconnection queue (§3 #2). 4) Add the 25-year O&M/degradation (§3 #5).

## Decision Tree: How do we finance post-2025?

1) Identify the live pathway (§3 #3). 2) Choose the ownership model. 3) Net the incentive, dated (§3 #8).

## Decision Tree: Is storage worth it?

1) Define the dispatch use-case (§3 #7). 2) Model the dispatch value. 3) Net against cost and size.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Model LCOE and project IRR** → use when: Model levelized cost of energy and project IRR together, on net cost after the live incentives, since they answer different questions. ([`../skills/model-lcoe-and-irr/SKILL.md`](../skills/model-lcoe-and-irr/SKILL.md))
- **Model the interconnection queue** → use when: Read the interconnection queue, study sequence, and likely upgrade allocation as the project's schedule and cost risk. ([`../skills/model-the-interconnection-queue/SKILL.md`](../skills/model-the-interconnection-queue/SKILL.md))
- **Structure to the live incentive** → use when: Structure the project around the incentive pathway that's actually available post-2025, with a date, instead of an expired one. ([`../skills/structure-the-incentive/SKILL.md`](../skills/structure-the-incentive/SKILL.md))
- **Read asset performance over life** → use when: Read availability, degradation, and O&M cost over the 25-year asset life so the IRR rests on real operations. ([`../skills/read-asset-performance/SKILL.md`](../skills/read-asset-performance/SKILL.md))
- **Value storage by dispatch** → use when: Value a battery on its dispatch use-case — arbitrage, demand-charge reduction, capacity — not a flat $/kWh. ([`../skills/value-storage-dispatch/SKILL.md`](../skills/value-storage-dispatch/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`renewables-engagement-lead`](../agents/renewables-engagement-lead.md)
- **Development** → [`solar-project-developer`](../agents/solar-project-developer.md)
- **The grid** → [`grid-interconnection-specialist`](../agents/grid-interconnection-specialist.md)
- **The numbers** → [`energy-finance-analyst`](../agents/energy-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. LCOE and project IRR are different questions — show both — if this is in question, apply §3 #1 before any method.
2. Interconnection is the schedule, and the schedule is the risk — if this is in question, apply §3 #2 before any method.
3. The incentive structure changed in 2025 — design to the live pathway — if this is in question, apply §3 #3 before any method.
4. Net cost after incentives is the real cost — model it explicitly — if this is in question, apply §3 #4 before any method.
5. A solar asset is a 25-year machine — degradation and O&M are first-class — if this is in question, apply §3 #5 before any method.
6. Production estimates are P50/P90, not a single number — if this is in question, apply §3 #6 before any method.
7. Storage changes the economics — value the dispatch, not just the kWh — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every cost and policy number — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
