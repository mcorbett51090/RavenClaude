---
description: "Tune chunk size, overlap, and structure-awareness against the eval and the context budget. Reach for this on a chunking question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Tune chunking

You are running `/ai-rag-engineering:tune-chunking` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Inspect the failing chunks — Are answering units (tables, sections) split or buried? (§3 #2)
2. Adjust size + overlap — Tune against recall@k, not a guessed default (§3 #2).
3. Add structure-awareness — Keep tables/sections intact; add metadata for pre-filtering (§3 #2).
4. Check the context budget — Size × top-k + overhead vs window via `ai_rag_engineering_calc.py chunk-budget` (§3 #5).

## Output
A chunking design tied to recall@k and the context budget. Traverse Tree 2 in the decision-trees file. See [`../skills/tune-chunking/SKILL.md`](../skills/tune-chunking/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / prompt PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
