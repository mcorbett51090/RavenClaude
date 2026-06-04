# Dental practice decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Take-home is down

1) Benchmark overhead (§3 #1). 2) Check the collection ratio (§3 #2). 3) Check case acceptance (§3 #3). 4) Read production per hour and hygiene (§3 #4, #5).

## Decision Tree: Big plans don't close

1) Measure acceptance by plan type (§3 #3). 2) Find the presentation/sequencing drop-off. 3) Re-sequence with financial options.

## Decision Tree: Margin erodes despite volume

1) Read effective fee by payer (§3 #6). 2) Map the PPO mix. 3) Decide the mix deliberately.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Benchmark overhead** → use when: Read overhead as a % of collections against the ~62% median before cutting any single cost, so the diagnosis targets the real driver. ([`../skills/benchmark-overhead/SKILL.md`](../skills/benchmark-overhead/SKILL.md))
- **Protect the collection ratio** → use when: Read banked-vs-produced dollars and recover the collection ratio toward 98%+, so production becomes income. ([`../skills/protect-the-collection-ratio/SKILL.md`](../skills/protect-the-collection-ratio/SKILL.md))
- **Lift case acceptance** → use when: Raise treatment-plan acceptance through presentation and sequencing rather than discounting. ([`../skills/lift-case-acceptance/SKILL.md`](../skills/lift-case-acceptance/SKILL.md))
- **Read production per hour** → use when: Read doctor and hygiene production per hour, not per day, to expose the real capacity story. ([`../skills/read-production-per-hour/SKILL.md`](../skills/read-production-per-hour/SKILL.md))
- **Manage the PPO payer mix** → use when: Read the effective fee by plan and manage PPO write-offs as a deliberate strategy, not an accident. ([`../skills/manage-the-payer-mix/SKILL.md`](../skills/manage-the-payer-mix/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`dental-practice-lead`](../agents/dental-practice-lead.md)
- **Case acceptance** → [`clinical-treatment-planner`](../agents/clinical-treatment-planner.md)
- **The revenue cycle** → [`dental-rcm-specialist`](../agents/dental-rcm-specialist.md)
- **The economics** → [`dental-operations-analyst`](../agents/dental-operations-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Overhead is the master margin number — if this is in question, apply §3 #1 before any method.
2. Collections, not production, pay the bills — if this is in question, apply §3 #2 before any method.
3. Case acceptance is presentation, not price — if this is in question, apply §3 #3 before any method.
4. Production per hour is the capacity lens — if this is in question, apply §3 #4 before any method.
5. The hygiene department is a profit engine, not a loss leader — if this is in question, apply §3 #5 before any method.
6. PPO write-offs are a strategy decision, not an accident — if this is in question, apply §3 #6 before any method.
7. Read the DSO-vs-independent position honestly — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
