# Game Development — Claude Code plugin

A production-and-design team for a game studio or indie team — it scopes to a vertical slice before a full build, designs core loops and economies that retain, runs production on milestones and risk burn-down, and reads live-ops on retention and monetization the way a team that ships and then operates a game must.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
game development depth on top.

## What it does

Scopes via vertical slice and risk burn-down, designs core loops and game economies for retention, plans production milestones, and reads live-ops on D1/D7/D30 retention and monetization. Produces scoping plans, design docs, and live-ops reads a studio acts on.

## Agents

- **`gamedev-producer`** — The engagement — scoping the project, framing the milestone plan, routing, and synthesizing a production plan.
- **`game-designer`** — Design — core loops, the game economy, progression, and the design doc.
- **`gameplay-engineer`** — Build feasibility — technical risk, prototyping, content pipelines, and engineering-cost reality, as technical decision-support.
- **`live-ops-analyst`** — The numbers — retention (D1/D7/D30), monetization (ARPDAU/conversion), the live-service roadmap, and the scorecard.

## Skills

- **`scope-to-vertical-slice`** — Scope the project to a vertical slice that proves the core loop is fun before scaling content, to de-risk the build. Reach for this at greenlight.
- **`design-the-core-loop`** — Design the second-to-second and session-to-session core loop before features, since retention lives there. Reach for this at the start of design.
- **`balance-the-economy`** — Design the economy as a system of sources, sinks, and progression pacing, not a price list, so it doesn't inflate or starve. Reach for this on an economy question.
- **`burn-down-risk`** — Track and burn down the riskiest unknowns (fun, tech, content cost) first, not just a task list, since scope kills games. Reach for this on the production plan.
- **`read-live-ops`** — Read retention (D1/D7/D30) and monetization together, gating monetization on retention, to operate the live game. Reach for this post-launch.

## Slash commands

- **`/game-development:scope-to-a-vertical-slice`** — Scope to a vertical slice
- **`/game-development:design-the-core-loop`** — Design the core loop
- **`/game-development:balance-the-game-economy`** — Balance the game economy

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install game-development@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a game engine, an analytics platform, or a publishing/legal authority — engine work, store policy, and contracts route to the relevant specialists. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
