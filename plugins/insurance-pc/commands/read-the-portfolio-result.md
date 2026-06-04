---
description: "Read the underwriting result by line of business, attritional-vs-cat and net-of-reinsurance, so the mix story is visible. Reach for this on a portfolio review."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Read the portfolio result

You are running `/insurance-pc:read-the-portfolio-result` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Decompose by line — NCR by line — e.g.
2. Strip cat per line — Separate attritional from cat by line (§3 #4).
3. Read net of reinsurance — Judge the result net where reinsurance matters.
4. Recommend the mix — Map growth/shrink decisions to the by-line result.

## Output
A by-line, attritional/cat, net-of-reinsurance portfolio read with a mix recommendation. See [`../skills/read-the-portfolio-result/SKILL.md`](../skills/read-the-portfolio-result/SKILL.md). Traverse the matching tree in [`../knowledge/pc-decision-trees.md`](../knowledge/pc-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
