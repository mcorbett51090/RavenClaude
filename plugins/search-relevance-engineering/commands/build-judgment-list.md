---
description: "Build graded relevance judgments (explicit or click-derived) and an offline harness before tuning. Reach for this when there's no eval."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build judgment list

You are running `/search-relevance-engineering:build-judgment-list` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Sample the query mix — Representative queries weighted by real traffic (§3 #7).
2. Grade relevance — Explicit graded labels or click-derived judgments, with position-bias caution (§3 #3 #6).
3. Build the offline harness — Reusable NDCG/MRR/precision@k harness over the judgment list (§3 #3).
4. Set the baseline — The current ranking's metrics — the bar every change must beat (§3 #1).

## Output
A graded judgment list and an offline harness with a recorded baseline. See [`../skills/build-judgment-list/SKILL.md`](../skills/build-judgment-list/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No query/user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
