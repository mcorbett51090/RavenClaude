# Clinical trial decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Enrollment is behind

1) Read the funnel — referral/eligibility/consent (§3 #5). 2) Stress-test feasibility (§3 #1). 3) Check site activation (§3 #4). 4) Check dropout (§3 #3).

## Decision Tree: Is this protocol enrollable?

1) Map eligibility to population (§3 #1). 2) Check site capacity. 3) Recommend criteria adjustments as decision-support.

## Decision Tree: Are we submission-ready?

1) Inventory documentation (§3 #7). 2) Check data quality. 3) Structure the eCTD and flag gaps.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Stress-test protocol feasibility** → use when: Stress-test eligibility criteria against the addressable population and site capacity before the protocol locks, since restrictive criteria are the biggest enrollment killer. ([`../skills/stress-test-feasibility/SKILL.md`](../skills/stress-test-feasibility/SKILL.md))
- **Plan the recruitment funnel** → use when: Plan recruitment as a costed funnel with a cost per stage, against the per-patient economics, instead of a hope. ([`../skills/plan-recruitment-funnel/SKILL.md`](../skills/plan-recruitment-funnel/SKILL.md))
- **Accelerate site activation** → use when: Sequence site selection, contracting, and start-up as the schedule's critical path to cut the activation delay. ([`../skills/accelerate-site-activation/SKILL.md`](../skills/accelerate-site-activation/SKILL.md))
- **Design for retention** → use when: Build retention into visit burden, schedule, and engagement to lower the ~30% dropout, instead of re-recruiting. ([`../skills/design-for-retention/SKILL.md`](../skills/design-for-retention/SKILL.md))
- **Read submission readiness** → use when: Read documentation completeness, data quality, and eCTD structure throughout the trial so the filing isn't a final-month scramble. ([`../skills/read-submission-readiness/SKILL.md`](../skills/read-submission-readiness/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`trials-engagement-lead`](../agents/trials-engagement-lead.md)
- **Feasibility** → [`protocol-design-specialist`](../agents/protocol-design-specialist.md)
- **Execution** → [`clinical-operations-manager`](../agents/clinical-operations-manager.md)
- **Submissions** → [`regulatory-submissions-specialist`](../agents/regulatory-submissions-specialist.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Protocol feasibility is set before the first patient — design for enrollment — if this is in question, apply §3 #1 before any method.
2. Recruitment is a costed pipeline, not a hope — if this is in question, apply §3 #2 before any method.
3. Retention is cheaper than re-recruitment — design for it — if this is in question, apply §3 #3 before any method.
4. Site activation is the schedule's long pole — if this is in question, apply §3 #4 before any method.
5. Enrollment is a rate, not a count — track the funnel — if this is in question, apply §3 #5 before any method.
6. Budget by phase and category — the shape differs — if this is in question, apply §3 #6 before any method.
7. The submission is built throughout, not at the end — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
