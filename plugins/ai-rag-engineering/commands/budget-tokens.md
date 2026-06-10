---
description: "Compute cost per request and right-size the context to fewest-high-precision chunks. Reach for this on a cost/context question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Budget tokens

You are running `/ai-rag-engineering:budget-tokens` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Count the tokens — Input (context + prompt) + output tokens per request (§3 #5).
2. Compute cost — Tokens × per-1k price × requests via `ai_rag_engineering_calc.py token-cost`; mark prices unverified (§3 #8).
3. Right-size context — Fewest high-precision chunks — guard against lost-in-the-middle (§3 #5).
4. Check the fit — Confirm chunk size × top-k fits the window via `ai_rag_engineering_calc.py chunk-budget` (§3 #5).

## Output
A token-cost read and a right-sized context recommendation with the monthly projection. See [`../skills/budget-tokens/SKILL.md`](../skills/budget-tokens/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / prompt PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
