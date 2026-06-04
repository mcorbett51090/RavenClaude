# Senior-care decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Margin is slipping

1) Read census flow (§3 #1). 2) Check acuity pricing (§3 #2). 3) Check acuity-based staffing/PPD (§3 #3). 4) Read labor/turnover (§3 #6).

## Decision Tree: Occupancy is dropping

1) Decompose move-out vs move-in (§3 #1). 2) Read the sales funnel (§3 #7). 3) Fix the conversion/time-to-move-in leak.

## Decision Tree: A quality/survey concern

1) Read survey readiness and incident patterns (§3 #4). 2) Map to operations. 3) Route clinical/regulatory items to the qualified authority.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Manage census flow** → use when: Read census as a flow of move-ins, move-outs, and length of stay, not a point number, so the right lever is pulled. ([`../skills/manage-census-flow/SKILL.md`](../skills/manage-census-flow/SKILL.md))
- **Price to acuity** → use when: Build acuity-based pricing that captures the care cost by level, instead of a flat rate, to protect margin. ([`../skills/price-to-acuity/SKILL.md`](../skills/price-to-acuity/SKILL.md))
- **Staff to acuity-based PPD** → use when: Build a staffing model on acuity-weighted hours-per-resident-day, not a fixed ratio, so labor matches need. ([`../skills/staff-to-acuity-ppd/SKILL.md`](../skills/staff-to-acuity-ppd/SKILL.md))
- **Read quality and compliance** → use when: Read survey readiness, incidents/falls, and quality measures as existential operational risk, as decision-support. ([`../skills/read-quality-and-compliance/SKILL.md`](../skills/read-quality-and-compliance/SKILL.md))
- **Quantify labor and turnover** → use when: Read labor cost, agency reliance, and turnover as quantified unit economics, since they drive both margin and quality. ([`../skills/quantify-labor-and-turnover/SKILL.md`](../skills/quantify-labor-and-turnover/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`senior-care-lead`](../agents/senior-care-lead.md)
- **Quality and compliance** → [`clinical-care-compliance-specialist`](../agents/clinical-care-compliance-specialist.md)
- **Census** → [`census-occupancy-strategist`](../agents/census-occupancy-strategist.md)
- **The numbers** → [`senior-care-finance-analyst`](../agents/senior-care-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Census is the revenue engine — manage the flow, not just the number — if this is in question, apply §3 #1 before any method.
2. Price to acuity, not a flat rate — if this is in question, apply §3 #2 before any method.
3. Staff to acuity-based hours-per-resident-day, not a fixed ratio — if this is in question, apply §3 #3 before any method.
4. Quality and compliance are the license and the reputation — track them — if this is in question, apply §3 #4 before any method.
5. Length of stay drives the economics — and it's shrinking — if this is in question, apply §3 #5 before any method.
6. Labor cost and turnover are a unit-economics issue, not just HR — if this is in question, apply §3 #6 before any method.
7. Move-in friction and sales conversion are the census levers — if this is in question, apply §3 #7 before any method.
8. Date and source any rate, benchmark, or regulation figure — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
