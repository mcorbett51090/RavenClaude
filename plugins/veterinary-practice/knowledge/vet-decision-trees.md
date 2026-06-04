# Veterinary practice decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Profit is down

1) Read production/ACT first (§3 #2). 2) Check capacity/utilization (§3 #3). 3) Check recommended-care acceptance (§3 #4). 4) Then the cost stack and fees (§3 #6).

## Decision Tree: Booked solid but revenue flat

1) Find the doctor bottleneck (§3 #3). 2) Fix the appointment template. 3) Tune the support ratio (§3 #7).

## Decision Tree: Sell to a consolidator?

1) Read the practice's economics honestly. 2) Frame against the consolidation market (§3 #5). 3) Compare value/control trade-offs.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Instrument production and ACT** → use when: Read practice revenue as production per DVM and average client transaction × visits, never one alone, so a revenue problem is diagnosed correctly. ([`../skills/instrument-production-and-act/SKILL.md`](../skills/instrument-production-and-act/SKILL.md))
- **Design a care protocol** → use when: Build an evidence-aligned, standardized care protocol as decision-support for the licensed DVM, to reduce unwarranted variation. ([`../skills/design-care-protocol/SKILL.md`](../skills/design-care-protocol/SKILL.md))
- **Unlock schedule capacity** → use when: Find the doctor bottleneck and fix the appointment template so a fully-booked practice can grow throughput. ([`../skills/unlock-schedule-capacity/SKILL.md`](../skills/unlock-schedule-capacity/SKILL.md))
- **Lift recommended-care compliance** → use when: Read recommended-care acceptance as a communication metric and raise it, instead of treating it as fixed demand. ([`../skills/lift-care-compliance/SKILL.md`](../skills/lift-care-compliance/SKILL.md))
- **Reprice the fee schedule** → use when: Reprice fees from the cost-of-service stack and medical value, not the neighbor's prices, to recover margin without losing position. ([`../skills/reprice-the-fee-schedule/SKILL.md`](../skills/reprice-the-fee-schedule/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`vet-practice-lead`](../agents/vet-practice-lead.md)
- **Standardized care** → [`clinical-protocol-specialist`](../agents/clinical-protocol-specialist.md)
- **Capacity and the floor** → [`practice-operations-manager`](../agents/practice-operations-manager.md)
- **The economics** → [`vet-finance-analyst`](../agents/vet-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Standardize protocols to kill unwarranted variation — if this is in question, apply §3 #1 before any method.
2. Production per DVM and ACT are the revenue engine — if this is in question, apply §3 #2 before any method.
3. Capacity gates revenue — the schedule is the constraint — if this is in question, apply §3 #3 before any method.
4. Compliance is medicine and revenue — track it — if this is in question, apply §3 #4 before any method.
5. Read the independent-vs-corporate position honestly — if this is in question, apply §3 #5 before any method.
6. Price to value and cost, not to the practice down the road — if this is in question, apply §3 #6 before any method.
7. Staff cost and DVM burnout are a unit-economics issue — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every market number — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
