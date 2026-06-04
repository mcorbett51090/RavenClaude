# Game-development decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: Will we ship on budget?

1) Scope to a vertical slice (§3 #1). 2) Burn down risk, not tasks (§3 #3). 3) Budget content cost-per-hour (§3 #6).

## Decision Tree: Retention is dropping

1) Read D1/D7/D30 and the drop-off (§3 #4). 2) Check the core loop (§3 #2). 3) Check the economy (§3 #5).

## Decision Tree: Is monetization healthy?

1) Confirm retention first (§3 #4). 2) Read ARPDAU/conversion. 3) Check the economy balance (§3 #5).

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Scope to a vertical slice** → use when: Scope the project to a vertical slice that proves the core loop is fun before scaling content, to de-risk the build. ([`../skills/scope-to-vertical-slice/SKILL.md`](../skills/scope-to-vertical-slice/SKILL.md))
- **Design the core loop** → use when: Design the second-to-second and session-to-session core loop before features, since retention lives there. ([`../skills/design-the-core-loop/SKILL.md`](../skills/design-the-core-loop/SKILL.md))
- **Balance the game economy** → use when: Design the economy as a system of sources, sinks, and progression pacing, not a price list, so it doesn't inflate or starve. ([`../skills/balance-the-economy/SKILL.md`](../skills/balance-the-economy/SKILL.md))
- **Burn down production risk** → use when: Track and burn down the riskiest unknowns (fun, tech, content cost) first, not just a task list, since scope kills games. ([`../skills/burn-down-risk/SKILL.md`](../skills/burn-down-risk/SKILL.md))
- **Read live-ops vital signs** → use when: Read retention (D1/D7/D30) and monetization together, gating monetization on retention, to operate the live game. ([`../skills/read-live-ops/SKILL.md`](../skills/read-live-ops/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`gamedev-producer`](../agents/gamedev-producer.md)
- **Design** → [`game-designer`](../agents/game-designer.md)
- **Build feasibility** → [`gameplay-engineer`](../agents/gameplay-engineer.md)
- **The numbers** → [`live-ops-analyst`](../agents/live-ops-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Prove the fun in a vertical slice before the full build — if this is in question, apply §3 #1 before any method.
2. The core loop is the product — design it before the features — if this is in question, apply §3 #2 before any method.
3. Scope is the enemy — burn down risk, not just tasks — if this is in question, apply §3 #3 before any method.
4. Retention before monetization — D1/D7/D30 are the vital signs — if this is in question, apply §3 #4 before any method.
5. Design the economy as a system, not a price list — if this is in question, apply §3 #5 before any method.
6. Content cost-per-hour is a real constraint — budget it — if this is in question, apply §3 #6 before any method.
7. Live-service is an operating model, not a launch — if this is in question, apply §3 #7 before any method.
8. Date and source any benchmark or market figure — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
