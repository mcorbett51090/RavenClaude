# Production decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Can we make this for the budget?

1) Define the deliverable spec (§3 #6). 2) Build the top-sheet (§3 #1). 3) Schedule to shoot days (§3 #2). 4) Size contingency to risk (§3 #4).

## Decision Tree: Will we deliver on time?

1) Map the post dependency chain (§3 #3). 2) Protect picture lock (§3 #5). 3) Find the critical path.

## Decision Tree: Are we going over?

1) Track cost vs bid (§3 #4). 2) Watch contingency burn. 3) Forecast overage exposure.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Build the top-sheet budget** → use when: Build the budget bottom-up to a top-sheet with a risk-sized contingency, so the number is defensible. ([`../skills/build-the-top-sheet/SKILL.md`](../skills/build-the-top-sheet/SKILL.md))
- **Schedule the shoot** → use when: Schedule to shoot days, locations, and cast availability with company moves and turnaround, not the calendar. ([`../skills/schedule-the-shoot/SKILL.md`](../skills/schedule-the-shoot/SKILL.md))
- **Sequence the post pipeline** → use when: Sequence post as a dependency chain keyed off picture lock, so the delivery date rests on the critical path. ([`../skills/sequence-the-post-pipeline/SKILL.md`](../skills/sequence-the-post-pipeline/SKILL.md))
- **Define the deliverables** → use when: Define the delivery spec (formats, masters, captions, QC) first, since it's the actual product. ([`../skills/define-the-deliverables/SKILL.md`](../skills/define-the-deliverables/SKILL.md))
- **Track cost vs bid** → use when: Track cost against the bid line by line and watch contingency burn, so overage is managed not discovered. ([`../skills/track-cost-vs-bid/SKILL.md`](../skills/track-cost-vs-bid/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`production-lead`](../agents/production-lead.md)
- **The day** → [`line-producer`](../agents/line-producer.md)
- **Post** → [`post-production-supervisor`](../agents/post-production-supervisor.md)
- **The numbers** → [`production-finance-analyst`](../agents/production-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Budget to a top-sheet with a real contingency — if this is in question, apply §3 #1 before any method.
2. Schedule to the shoot day, not the calendar — if this is in question, apply §3 #2 before any method.
3. Post is a dependency chain — sequence it, don't parallelize blindly — if this is in question, apply §3 #3 before any method.
4. Contingency and overage are managed, not hoped — if this is in question, apply §3 #4 before any method.
5. Locked picture is the gate everything downstream waits on — if this is in question, apply §3 #5 before any method.
6. Deliverables and specs are the actual product — define them first — if this is in question, apply §3 #6 before any method.
7. Crew, gear, and location costs are rate × time × risk — build them up — if this is in question, apply §3 #7 before any method.
8. Date and source any rate, union, or market figure — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
