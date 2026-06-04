---
description: "Read empty miles and truck utilization and build a routing/backhaul plan to lift the loaded-mile ratio. Reach for this when rate-per-mile looks fine but margin doesn't."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Reduce deadhead and raise utilization

You are running `/fleet-logistics:reduce-deadhead-and-raise-utilization` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure deadhead and utilization — Empty-mile % and revenue-per-truck-per-day by lane (§3 #3).
2. Find the backhaul — Identify lanes with backhaul/repositioning opportunity.
3. Re-plan routing — Build the dispatch/backhaul plan to raise the loaded-mile ratio.
4. Price the lane — Price each lane against CPM including deadhead (§3 #6).

## Output
A deadhead/utilization read, a backhaul plan, and lane pricing against CPM. See [`../skills/reduce-deadhead/SKILL.md`](../skills/reduce-deadhead/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
