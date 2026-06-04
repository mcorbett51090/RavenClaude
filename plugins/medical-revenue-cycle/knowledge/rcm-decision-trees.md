# RCM decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Cash is slipping

1) Read net collection rate (§3 #4). 2) Read days-in-A/R by bucket (§3 #3). 3) Read first-pass/denial rate (§3 #2). 4) Categorize denials by root cause (§3 #5).

## Decision Tree: Denial rate is high

1) Categorize by root cause and owner (§3 #5). 2) Push eligibility/auth upstream (§3 #6). 3) Coding denials → documentation, not up-code (§3 #7).

## Decision Tree: A/R is piling up

1) Segment by bucket and payer (§3 #3). 2) Flag timely-filing risk. 3) Prioritize by recoverable dollars.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Prevent denials at the root** → use when: Categorize denials by root cause and owner and push fixes upstream to registration and authorization, instead of only appealing. ([`../skills/prevent-denials/SKILL.md`](../skills/prevent-denials/SKILL.md))
- **Read the cash cycle** → use when: Read net collection rate, first-pass resolution, and days-in-A/R together, against benchmark, so a cash problem is diagnosed correctly. ([`../skills/read-the-cash-cycle/SKILL.md`](../skills/read-the-cash-cycle/SKILL.md))
- **Work down aged A/R** → use when: Prioritize an A/R work-down by aging bucket, payer, and recoverable dollars, with timely-filing risk first. ([`../skills/work-down-ar/SKILL.md`](../skills/work-down-ar/SKILL.md))
- **Read coding-driven denials** → use when: Trace coding denials to documentation, code selection, or modifier use as decision-support, never to up-coding. ([`../skills/read-coding-denials/SKILL.md`](../skills/read-coding-denials/SKILL.md))
- **Build an RCM scorecard** → use when: Build a net-collection-led RCM scorecard with first-pass, denial-by-category, and days-in-A/R, each defined and baselined. ([`../skills/build-rcm-scorecard/SKILL.md`](../skills/build-rcm-scorecard/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`rcm-engagement-lead`](../agents/rcm-engagement-lead.md)
- **Coding accuracy** → [`medical-coding-specialist`](../agents/medical-coding-specialist.md)
- **Denial prevention and A/R** → [`denials-management-specialist`](../agents/denials-management-specialist.md)
- **The metrics** → [`rcm-analytics-analyst`](../agents/rcm-analytics-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Prevent denials; don't just appeal them — if this is in question, apply §3 #1 before any method.
2. First-pass resolution is the master efficiency number — if this is in question, apply §3 #2 before any method.
3. Days in A/R is the cash-cycle headline — if this is in question, apply §3 #3 before any method.
4. Net collection rate, not gross, measures the cycle — if this is in question, apply §3 #4 before any method.
5. Denials have a root cause and an owner — categorize them — if this is in question, apply §3 #5 before any method.
6. Front-end errors are back-end denials — fix them upstream — if this is in question, apply §3 #6 before any method.
7. Coding accuracy is decision-support, not autopilot — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
