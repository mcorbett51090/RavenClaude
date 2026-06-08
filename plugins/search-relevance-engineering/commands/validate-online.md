---
description: "Confirm an offline relevance win with an online A/B on CTR/conversion before declaring victory. Reach for this after an offline gain."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Validate online

You are running `/search-relevance-engineering:validate-online` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Confirm the offline win — A clear NDCG/MRR improvement on the judgment list first (§3 #1).
2. Design the A/B — Control vs variant on a real metric (CTR/conversion), powered and bias-aware (§3 #6).
3. Read the online result — Did the offline gain move the user metric? It may not (§3 #6).
4. Ship only on confirmation — Promote the variant only if online confirms; otherwise keep digging (§3 #6).

## Output
An online A/B result confirming (or refuting) the offline relevance gain. Traverse Tree 1 in the decision-trees file. See [`../skills/validate-online/SKILL.md`](../skills/validate-online/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No query/user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
