# Restaurant decision trees

Which analysis for which symptom — traverse top-to-bottom before picking a method.

## Decision Tree: This store is losing money

1) Read prime cost first (§3 #1). 2) Split food vs labor. 3) Food → theoretical-vs-actual gap (§3 #2); labor → daypart ratio (§3 #4). 4) Then menu mix (§3 #3).

## Decision Tree: Margins are thin but sales are fine

1) Engineer the menu on contribution margin (§3 #5). 2) Check comps/voids/waste (§3 #6). 3) Resist a price cut as the first lever (§3 #3).

## Decision Tree: One store lags the others

1) Normalize for format/daypart (§3 #7). 2) Rank on prime cost. 3) Map top-quartile practices to the laggard.

## How to read these trees

Traverse top-to-bottom and stop at the first matching branch — the order encodes the cheap-checks-before-expensive-checks discipline (§3). Each leaf names a skill, a specialist, or a house-opinion to apply. Never skip a higher branch because a lower one looks more interesting; a denominator, seasonal, or definitional artifact masquerades as a finding more often than not.

## Decision Tree: Which skill for which task

- **Read prime cost** → use when: Lead any four-wall read with prime cost (food + labor) before decomposing either half, so the master number frames the diagnosis. ([`../skills/read-prime-cost/SKILL.md`](../skills/read-prime-cost/SKILL.md))
- **Engineer the menu** → use when: Place every item on the contribution-margin × popularity matrix and move the mix, instead of cutting prices, to raise margin. ([`../skills/engineer-the-menu/SKILL.md`](../skills/engineer-the-menu/SKILL.md))
- **Close the food-cost gap** → use when: Decompose actual vs theoretical food cost into waste, portioning, price, and theft, so the fix targets the real driver. ([`../skills/close-the-food-cost-gap/SKILL.md`](../skills/close-the-food-cost-gap/SKILL.md))
- **Schedule labor to demand** → use when: Build a labor plan to forecast demand by daypart that holds the service line, so a labor cut doesn't cost more than it saves. ([`../skills/schedule-to-demand/SKILL.md`](../skills/schedule-to-demand/SKILL.md))
- **Rank multi-unit variance** → use when: Rank comparable units against each other, normalized for format and daypart, to find where the margin actually is. ([`../skills/rank-multi-unit/SKILL.md`](../skills/rank-multi-unit/SKILL.md))

## Decision Tree: Which specialist owns this

- **The engagement** → [`restaurant-engagement-lead`](../agents/restaurant-engagement-lead.md)
- **The menu and food cost** → [`menu-cost-engineer`](../agents/menu-cost-engineer.md)
- **Service and labor** → [`foh-boh-operations-specialist`](../agents/foh-boh-operations-specialist.md)
- **The four-wall P&L** → [`restaurant-finance-analyst`](../agents/restaurant-finance-analyst.md)

When two leaves apply, route to the **lead** first to scope and sequence — overlapping symptoms usually mean two drivers at once, and the lead keeps the analysis from collapsing into a single-cause story.

## Decision Tree: Which house-opinion gates the call

Before picking any method, check whether one of the standing biases (§3) already decides the framing:

1. Prime cost is the master number — if this is in question, apply §3 #1 before any method.
2. Food cost is judged against theoretical, not last month — if this is in question, apply §3 #2 before any method.
3. Engineer the menu on margin AND popularity, never price — if this is in question, apply §3 #3 before any method.
4. Labor is a ratio to sales, with a floor — if this is in question, apply §3 #4 before any method.
5. Contribution margin per item beats food-cost % — if this is in question, apply §3 #5 before any method.
6. Comps, voids, and waste are a control system, not noise — if this is in question, apply §3 #6 before any method.
7. Multi-unit variance is the signal — rank stores against themselves — if this is in question, apply §3 #7 before any method.
8. Cite the source and date for every benchmark — if this is in question, apply §3 #8 before any method.

## Escalation & guardrails

- Anything touching client PII / regulated records → stop and route to `ravenclaude-core` `security-reviewer`.
- Any external figure entering a deliverable → carry a source URL + retrieval date, or mark it `[unverified — training knowledge]` / `[ESTIMATE]` (§3, final house opinion).
- A recommendation ships only with an owner, a date, and an expected metric movement.
## Sourcing note

Figures in this file are from the author's domain knowledge and are marked `[unverified — training knowledge]` or `[ESTIMATE]` at point of use. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
