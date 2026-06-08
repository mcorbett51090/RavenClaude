---
description: "Compute the four DORA keys and classify the org against the bands with windows and baselines. Reach for this on a DevEx-measurement question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Classify DORA

You are running `/platform-engineering-idp:classify-dora` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Pull the four keys — Deploy frequency, lead time for change, change-failure rate, MTTR over a fixed window.
2. Classify each — Map each key to elite/high/medium/low via `platform_engineering_idp_calc.py dora` (§3 #3).
3. Attach windows + baselines — Every key carries a window and a prior baseline, or it doesn't ship (§3 #3).
4. Name the binding constraint — The weakest key is the lever; pair it with survey signal, not instead of it.

## Output
A classified four-key DORA read with windows, baselines, and the binding constraint named. Traverse Tree 1 in the decision-trees file. See [`../skills/classify-dora/SKILL.md`](../skills/classify-dora/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No internal credentials/PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
