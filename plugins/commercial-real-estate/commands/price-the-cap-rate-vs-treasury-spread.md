---
description: "Frame a cap rate as a risk premium over the 10-yr Treasury, not an absolute level, so a 'compression' is read correctly. Reach for this whenever a cap rate enters a memo."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Price the cap-rate-vs-Treasury spread

You are running `/commercial-real-estate:price-the-cap-rate-vs-treasury-spread` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Compute the spread — Cap rate minus the current 10-yr Treasury yield — the risk premium you're actually buying (§3 #3).
2. Place it historically — Compare the spread to its long-run range; a thin spread (e.g.
3. Decompose a move — When the cap rate moves, attribute it to the rate leg vs the premium leg — they have opposite implications.
4. Carry the date — Every cap-rate and Treasury figure gets a retrieval date; these move quarterly (§3 #8).

## Output
A spread, its historical percentile, an attribution of any move, and the dated sources. See [`../skills/price-the-cap-rate-spread/SKILL.md`](../skills/price-the-cap-rate-spread/SKILL.md). Traverse the matching tree in [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
