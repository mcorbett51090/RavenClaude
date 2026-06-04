---
description: "Build a net-collection-led RCM scorecard with first-pass, denial-by-category, and days-in-A/R, each defined and baselined. Reach for this to instrument the cycle."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build an RCM scorecard

You are running `/medical-revenue-cycle:build-an-rcm-scorecard` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Lead with net collection rate — Defined against allowed, with window and baseline (§3 #4).
2. Add the efficiency metrics — First-pass resolution and clean-claim rate (§3 #2).
3. Add denial analytics — Denial rate by category and payer (§3 #5).
4. Add the cash-cycle metric — Days-in-A/R by aging bucket (§3 #3).

## Output
A net-collection-led RCM scorecard with efficiency, denial, and A/R metrics, each defined and baselined. See [`../skills/build-rcm-scorecard/SKILL.md`](../skills/build-rcm-scorecard/SKILL.md). Traverse the matching tree in [`../knowledge/rcm-decision-trees.md`](../knowledge/rcm-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
