---
description: "Inventory idle/orphaned/oversized/zombie resources and rank the pure-savings wins. Reach for this first on any cost spike."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Harvest waste

You are running `/finops-cloud-cost:harvest-waste` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Inventory waste — Idle instances, orphaned volumes/IPs, oversized resources, zombie environments.
2. Rank by dollars — Pure savings with no trade-off, biggest first (§3 #5).
3. Harvest before discounts — Kill waste BEFORE negotiating commitments or re-architecting (§3 #4 #5).
4. Confirm no dependency — A resource that looks idle but serves a rare job is not waste — verify.

## Output
A ranked waste inventory with the pure-savings dollars and the harvest order. See [`../skills/harvest-waste/SKILL.md`](../skills/harvest-waste/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No billing/account PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
