# Fundraising decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Revenue is flat

1) Read retention by cohort first (§3 #1). 2) Read cost-per-dollar by channel (§3 #4). 3) Check the grant pipeline (§3 #2) and major-gift cycle (§3 #5).

## Decision Tree: Should we pursue this grant?

1) Score funder fit (§3 #2). 2) Weigh effort vs odds. 3) Go/no-go and pipeline.

## Decision Tree: Cultivation is spread thin

1) Segment by RFM (§3 #3). 2) Tier the base. 3) Concentrate hours on movable high-value donors.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Protect donor retention** → use when: Read donor retention by cohort and fix the leaky bucket before pouring in acquisition, since retention is ~7x cheaper than acquisition. ([`../skills/protect-donor-retention/SKILL.md`](../skills/protect-donor-retention/SKILL.md))
- **Qualify the funder** → use when: Score a grant opportunity on funder fit before writing, so effort goes where alignment is. ([`../skills/qualify-the-funder/SKILL.md`](../skills/qualify-the-funder/SKILL.md))
- **Run the cultivation cycle** → use when: Move a donor through identification, qualification, cultivation, solicitation, and stewardship rather than jumping to the ask. ([`../skills/run-the-cultivation-cycle/SKILL.md`](../skills/run-the-cultivation-cycle/SKILL.md))
- **Segment the donor base** → use when: Segment donors by value, recency, and engagement (RFM-style) to direct cultivation hours where they pay. ([`../skills/segment-the-donor-base/SKILL.md`](../skills/segment-the-donor-base/SKILL.md))
- **Read cost-per-dollar by channel** → use when: Compute cost-to-raise-a-dollar per channel, never blended, so the subsidizing channel is visible. ([`../skills/read-cost-per-dollar/SKILL.md`](../skills/read-cost-per-dollar/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`development-lead`](../agents/development-lead.md)
- **Grants** → [`grant-writer`](../agents/grant-writer.md)
- **Major gifts and donors** → [`major-gifts-strategist`](../agents/major-gifts-strategist.md)
- **The numbers** → [`nonprofit-finance-analyst`](../agents/nonprofit-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Retention is the cheapest dollar — protect it first — if this is in question, apply §3 #1 before any method.
2. Qualify grants on funder fit before writing — if this is in question, apply §3 #2 before any method.
3. Segment donors by value, recency, and engagement — if this is in question, apply §3 #3 before any method.
4. Read cost-to-raise-a-dollar by channel, not blended — if this is in question, apply §3 #4 before any method.
5. Major gifts are a cultivation cycle, not an ask — if this is in question, apply §3 #5 before any method.
6. Restricted vs unrestricted is a sustainability question — if this is in question, apply §3 #6 before any method.
7. Stewardship is fundraising — the next gift starts at thank-you — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
