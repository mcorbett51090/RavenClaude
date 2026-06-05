# Technical debt in the core loop compounds like interest

**Status:** Pattern
**Domain:** Game engineering and production
**Applies to:** `game-development`

---

## Why this exists

Technical debt accrues in every system of a game, but debt in the core loop is uniquely expensive. Every feature, every balance pass, every live-ops event, and every new content type touches the core loop — which means core-loop technical debt taxes every subsequent piece of work. A collision system that needs to be reworked will be reworked while three other teams are also depending on it. A character-controller hack that was "good enough for the vertical slice" becomes a constraint that blocks better feel, multiplayer, and animations for the rest of the project. The gameplay engineer's first job is to flag core-loop debt early — when the cost of addressing it is low — not late, when the entire content pipeline has been built on top of it.

## How to apply

At the end of the vertical slice phase, conduct a deliberate core-loop debt audit before scaling content or features. Classify debt by blast radius and address high-blast-radius items before the alpha build.

```
Core-loop debt audit (post-vertical-slice):

  System to audit | Debt item | Blast radius | Cost to fix now | Cost to fix at alpha
  ---|---|---|---|---
  Movement / collision | hack description | HIGH | 2 days | 3 weeks
  State machine | temporary coupling | MEDIUM | 1 day | 1 week
  Economy system | placeholder formula | MEDIUM | 3 days | 2 weeks
  Save/checkpoint | deferred | LOW | 1 week | 1 week

  Blast radius classification:
    HIGH: other systems depend on this — changing it later requires touching 3+ subsystems
    MEDIUM: isolated debt — changing later requires touching 1–2 subsystems
    LOW: self-contained — can be addressed at any time without cascading changes

  Action rule:
    HIGH blast radius → address before content scaling begins
    MEDIUM blast radius → schedule in the next milestone
    LOW blast radius → tech-debt backlog with no urgency gate
```

**Do:**
- Run the core-loop debt audit at the end of the vertical slice, before content scaling.
- Include blast-radius classification in every sprint retrospective for core systems.
- Give the gameplay engineer authority to raise HIGH-blast-radius debt to the producer as a milestone risk.

**Don't:**
- Defer HIGH-blast-radius core-loop debt past the alpha milestone.
- Treat all technical debt as equal — a collision-system hack and a UI string-formatting issue are not the same category of risk.
- Let a "we'll fix it later" comment survive without a classification and a timeline.

## Edge cases / when the rule does NOT apply

Game jam and prototype builds have intentional technical debt by design — the goal is speed, not maintainability. The rule applies when the project transitions from prototype to production scope. For engine/platform ports, the audit is run before the content migration begins, not after.

## See also

- [`../agents/gameplay-engineer.md`](../agents/gameplay-engineer.md) — owns the technical feasibility assessment and the core-loop debt audit.
- [`./scope-is-the-enemy-burn-down-risk-not-just-tasks.md`](./scope-is-the-enemy-burn-down-risk-not-just-tasks.md) — the companion rule on treating unknowns as production risk.

## Provenance

Codifies the core-loop-first debt-audit practice grounded in the team's §3 #2 house opinion ("the core loop is the product — design it before the features"). The post-vertical-slice debt audit is the standard check before content scaling; skipping it is how the "we'll fix it later" hack becomes a two-year drag.

---

_Last reviewed: 2026-06-05 by `claude`_
