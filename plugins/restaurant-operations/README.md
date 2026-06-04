# Restaurant Operations — Claude Code plugin

An operations-and-unit-economics team for an independent or multi-unit restaurant operator — it manages prime cost (food + labor), engineers the menu by contribution margin and popularity, controls food cost against theoretical, and reads the P&L the way a GM who lives the four-wall margin does.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
restaurant operations depth on top.

## What it does

Holds prime cost as the master number, engineers the menu on the margin-vs-popularity matrix, separates actual food cost from theoretical to find the variance, and instruments labor against sales without slipping below the service line. Produces P&L reads, menu re-engineering, and store-ops scorecards an operator acts on.

## Agents

- **`restaurant-engagement-lead`** — The engagement — scoping the operator's problem, framing the four-wall read, routing to a specialist, and synthesizing an action plan.
- **`menu-cost-engineer`** — The menu and food cost — recipe costing, theoretical vs actual, the engineering matrix, and contribution-margin pricing.
- **`foh-boh-operations-specialist`** — Service and labor — scheduling to demand, labor % by daypart, throughput, comps/voids/waste controls, and the service line.
- **`restaurant-finance-analyst`** — The four-wall P&L — prime cost, the full margin bridge, multi-unit variance, and the scorecard.

## Skills

- **`read-prime-cost`** — Lead any four-wall read with prime cost (food + labor) before decomposing either half, so the master number frames the diagnosis. Reach for this on any margin problem.
- **`engineer-the-menu`** — Place every item on the contribution-margin × popularity matrix and move the mix, instead of cutting prices, to raise margin. Reach for this when margins are thin.
- **`close-the-food-cost-gap`** — Decompose actual vs theoretical food cost into waste, portioning, price, and theft, so the fix targets the real driver. Reach for this when food cost moves.
- **`schedule-to-demand`** — Build a labor plan to forecast demand by daypart that holds the service line, so a labor cut doesn't cost more than it saves. Reach for this on a labor problem.
- **`rank-multi-unit`** — Rank comparable units against each other, normalized for format and daypart, to find where the margin actually is. Reach for this on a portfolio review.

## Slash commands

- **`/restaurant-operations:read-prime-cost`** — Read prime cost
- **`/restaurant-operations:engineer-the-menu`** — Engineer the menu
- **`/restaurant-operations:close-the-food-cost-gap`** — Close the food-cost gap
- **`/restaurant-operations:schedule-labor-to-demand`** — Schedule labor to demand
- **`/restaurant-operations:rank-multi-unit-variance`** — Rank multi-unit variance

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install restaurant-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a POS, an accounting system, or a food-safety authority, and gives no legal, tax, or health-code rulings — it flags where those questions live. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
