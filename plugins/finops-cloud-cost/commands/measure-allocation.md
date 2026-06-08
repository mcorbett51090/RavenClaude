---
description: "Read allocation coverage as tagged ÷ total, size the ungoverned pile, and design showback. Reach for this on an allocation question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Measure allocation

You are running `/finops-cloud-cost:measure-allocation` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull tagged vs total — Attributed spend ÷ total spend over a fixed window (§3 #1).
2. Size the gap — The ungoverned pile is the un-allocatable spend; rank the biggest untagged sources.
3. Design showback — Visibility to owning teams first; chargeback later — showback drives most behavior (§3 #6).
4. Set a coverage target — A usable allocation threshold before optimizing anything (§3 #1).

## Output
An allocation-coverage read with the ungoverned gap sized and showback designed. Traverse Tree 1 in the decision-trees file. See [`../skills/measure-allocation/SKILL.md`](../skills/measure-allocation/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No billing/account PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
