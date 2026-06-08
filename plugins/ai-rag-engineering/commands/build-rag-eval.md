---
description: "Build a judgment set and measure recall@k, precision@k, faithfulness, and answer-relevance with a baseline. Reach for this before shipping any change."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Build RAG eval

You are running `/ai-rag-engineering:build-rag-eval` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the judgment set — Representative queries with the relevant passages and ideal answers labeled (§3 #3).
2. Measure retrieval — Recall@k and precision@k via `ai_rag_engineering_calc.py retrieval-eval` (§3 #1 #3).
3. Measure generation — Faithfulness (grounded?) and answer-relevance (addresses query?) (§3 #3 #7).
4. Baseline before changing — Record the baseline; every change reports a before/after delta — no eval, no ship (§3 #3).

## Output
An eval harness with recall@k, precision@k, faithfulness, answer-relevance, and a baseline. Traverse Tree 1 in the decision-trees file. See [`../skills/build-rag-eval/SKILL.md`](../skills/build-rag-eval/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / prompt PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
