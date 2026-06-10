---
description: "Separate retrieval failure from generation failure by measuring recall@k before touching the model. Reach for this first on wrong answers."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Diagnose retrieval

You are running `/ai-rag-engineering:diagnose-retrieval` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Measure recall@k — Is the relevant passage in the top-k? via `ai_rag_engineering_calc.py retrieval-eval` (§3 #1).
2. Split the failure mode — Low recall = retrieval bug; high recall + wrong answer = generation/grounding bug (§3 #1 #7).
3. Check hybrid — Try BM25 + vector fusion on the failing queries, especially keyword-heavy ones (§3 #6).
4. Fix the binding stage first — Retrieval before generation — don't swap the model on a retrieval bug (§3 #1).

## Output
A failure-mode split (retrieval vs generation) with the first fix named. Traverse Tree 2 in the decision-trees file. See [`../skills/diagnose-retrieval/SKILL.md`](../skills/diagnose-retrieval/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / prompt PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
