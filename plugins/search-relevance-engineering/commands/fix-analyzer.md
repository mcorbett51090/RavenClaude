---
description: "Root-cause a relevance bug in tokenization/analysis/mapping before touching the ranking formula. Reach for this on a no-match or wrong-match bug."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Fix analyzer

You are running `/search-relevance-engineering:fix-analyzer` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Reproduce the match failure — Trace how the query and document are analyzed/tokenized (§3 #2).
2. Check the mapping — Field types, analyzers, stemming, synonyms — does it match as intended? (§3 #2)
3. Secure recall first — Fix matching/query expansion so the right doc is retrieved (§3 #5).
4. Re-measure relevance — Confirm the fix on NDCG, don't trust the spot-check (§3 #1).

## Output
An analyzer/mapping root-cause and recall fix with the relevance re-measured. Traverse Tree 2 in the decision-trees file. See [`../skills/fix-analyzer/SKILL.md`](../skills/fix-analyzer/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No query/user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
