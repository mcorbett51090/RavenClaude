---
name: Game Theory Basics
description: >-
  Use this when multiple agents or parties have incentives — sketch payoffs,
  dominant strategies, and equilibrium intuition for coordination, gates, and
  escalation.
---

# Game Theory Basics

Companion to RavenClaude Core and Quantitative Problem Solving.

## Stance

1. Payoffs first — who gets what under each outcome.
2. Dominant strategy if it exists; else mutual best replies / equilibrium intuition.
3. Not everything is a game — if the opponent is nature or a bug, use Quantitative Problem Solving instead.
4. Cooperate by default inside the team — hiding failure or bypassing CoS/gates is negative-sum for Matthew.

## Workflow 1 — Normal-form sketch

Players, actions, payoffs (ordinal is fine). Classic Prisoner's Dilemma when Temptation > Reward > Punishment > Sucker. Inside Matthew's bot team, set long-run payoffs so honest escalate / share-evidence wins.

## Workflow 2 — Checklist

1. Who are the players?
2. What moves exist this turn?
3. Payoffs for Matthew first, then each player
4. Is there a dominant strategy?
5. If simultaneous: reasonable Nash / mutual best reply?
6. If sequential: backward induction from the last node
7. Prefer strategies incentive-compatible with wall escalation and gates

## Workflow 3 — Grok Bot mappings

- Hide wall vs escalate to CoS: cooperate = escalate with evidence
- Two bots disagree: forge panels + critic, not volume war
- Money/delete approval: do not bypass; waiting is the move
- API rate limits: repeated game — backoff sustains access

## Deliverable shape

Players + moves; payoff notes; recommended strategy in one sentence; what would change it.

## Anti-patterns

Treating a bug as an adversary when nature models suffice; defecting against process to save tokens; assuming zero-sum when a correct fix grows the pie.

## Credit

Lightweight companion for RavenClaude Core multi-agent / human loops.
