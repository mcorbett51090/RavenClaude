# DTC decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Growing but not profitable

1) Read LTV:CAC and contribution margin (§3 #1, #2). 2) Split CAC by channel (§3 #5). 3) Check retention (§3 #3). 4) Cost the returns (§3 #6).

## Decision Tree: Conversion is low

1) Map the funnel (§3 #4). 2) Find the drop-off stage. 3) Attribute to traffic, product page, or checkout.

## Decision Tree: CAC is climbing

1) Split CAC by channel and cohort (§3 #5). 2) Match to cohort LTV (§3 #1). 3) Reallocate to efficient channels.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Read LTV:CAC and contribution margin** → use when: Read LTV:CAC against the 3:1 line and contribution margin after the real costs, so a profitability problem is diagnosed correctly. ([`../skills/read-ltv-cac/SKILL.md`](../skills/read-ltv-cac/SKILL.md))
- **Diagnose the conversion funnel** → use when: Locate a conversion problem by funnel stage — traffic, product page, cart, checkout — instead of reading the headline rate. ([`../skills/diagnose-the-funnel/SKILL.md`](../skills/diagnose-the-funnel/SKILL.md))
- **Build the retention engine** → use when: Read cohort retention and the repeat rate and build the second-purchase engine, since retention compounds LTV. ([`../skills/build-the-retention-engine/SKILL.md`](../skills/build-the-retention-engine/SKILL.md))
- **Manage CAC by channel** → use when: Read CAC by channel and cohort and allocate budget to efficiency, instead of a blended number. ([`../skills/manage-cac-by-channel/SKILL.md`](../skills/manage-cac-by-channel/SKILL.md))
- **Cost the returns** → use when: Read return rate and its full cost as a contribution-margin line, so a high-return category isn't mistaken for a winner. ([`../skills/cost-the-returns/SKILL.md`](../skills/cost-the-returns/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`ecommerce-lead`](../agents/ecommerce-lead.md)
- **Product and conversion** → [`merchandising-specialist`](../agents/merchandising-specialist.md)
- **Acquisition** → [`performance-marketing-strategist`](../agents/performance-marketing-strategist.md)
- **The numbers** → [`retention-analytics-analyst`](../agents/retention-analytics-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. LTV:CAC is the master ratio — 3:1 is the line — if this is in question, apply §3 #1 before any method.
2. Contribution margin, not revenue, is the scoreboard — if this is in question, apply §3 #2 before any method.
3. Retention is the profit engine — the second purchase is everything — if this is in question, apply §3 #3 before any method.
4. Read the conversion funnel, not the conversion rate — if this is in question, apply §3 #4 before any method.
5. CAC is a blended lie — read it by channel and by cohort — if this is in question, apply §3 #5 before any method.
6. Returns are a margin line, not a customer-service line — if this is in question, apply §3 #6 before any method.
7. AOV and frequency are levers you design, not constants — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
