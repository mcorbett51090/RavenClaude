# Trade-contracting decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Busy but not profitable

1) Check the loaded labor rate (§3 #1). 2) Check flat-rate vs guessed hours (§3 #2). 3) Read billable-hour efficiency (§3 #3). 4) Read first-time-fix (§3 #4).

## Decision Tree: Techs aren't billing enough

1) Measure the billable ratio (§3 #3). 2) Locate non-billable time. 3) Fix dispatch and stocking (§3 #6).

## Decision Tree: Should I spend on marketing?

1) Read close rate and average ticket (§3 #7). 2) Find the no-spend revenue gap. 3) Improve option-presentation first.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Build the loaded labor rate** → use when: Build a billable labor rate that absorbs wage, burden, vehicle, tools, insurance, and overhead, so every hour sold makes money. ([`../skills/build-the-loaded-rate/SKILL.md`](../skills/build-the-loaded-rate/SKILL.md))
- **Build the flat-rate book** → use when: Build a flat-rate price book from loaded labor and real material cost with good/better/best options, so service pricing protects margin. ([`../skills/build-flat-rate-book/SKILL.md`](../skills/build-flat-rate-book/SKILL.md))
- **Raise billable-hour efficiency** → use when: Read the billable-hour ratio and cut non-billable drive, restock, and rework time, since billable efficiency is the field's master number. ([`../skills/raise-billable-efficiency/SKILL.md`](../skills/raise-billable-efficiency/SKILL.md))
- **Cut the callback rate** → use when: Read first-time-fix and quantify the callback labor cost, then fix truck stocking and diagnosis, since a callback is a free truck roll. ([`../skills/cut-callbacks/SKILL.md`](../skills/cut-callbacks/SKILL.md))
- **Read the sales levers** → use when: Read close rate and average ticket and option-presentation, since they move revenue more than lead volume. ([`../skills/read-the-sales-levers/SKILL.md`](../skills/read-the-sales-levers/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`trades-engagement-lead`](../agents/trades-engagement-lead.md)
- **Estimates and pricing** → [`estimating-specialist`](../agents/estimating-specialist.md)
- **The field** → [`field-operations-specialist`](../agents/field-operations-specialist.md)
- **The numbers** → [`trade-business-analyst`](../agents/trade-business-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Estimate to a fully-loaded labor rate, not a wage — if this is in question, apply §3 #1 before any method.
2. Price service on a flat-rate book, not guessed hours — if this is in question, apply §3 #2 before any method.
3. Billable-hour efficiency is the field's master number — if this is in question, apply §3 #3 before any method.
4. First-time-fix and callback rate are margin, not just quality — if this is in question, apply §3 #4 before any method.
5. Material cost is the real cost plus waste plus markup — name all three — if this is in question, apply §3 #5 before any method.
6. The truck is a profit center with a utilization number — if this is in question, apply §3 #6 before any method.
7. Quote close rate and average ticket are the sales levers — if this is in question, apply §3 #7 before any method.
8. Date and source any wage, material, or market figure — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
