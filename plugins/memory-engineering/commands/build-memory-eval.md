---
description: "Prove a memory system earns its write path — golden set with provenance, judged failure modes, the runnable bake-off, and cost per correct answer. Reach for this before adopting or retiring any memory system."
argument-hint: "[the situation, e.g. the store / agent / workload in question]"
---

# Build memory eval

You are running `/memory-engineering:build-memory-eval` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Build the golden set first — Query, expected answer, the session the fact was established, how many sessions ago, provenance and date; cover the long horizon deliberately (§3 #8).
2. Label every item with its failure mode — Stale fact, unresolved contradiction, confabulated recall, poisoned recall, over-retention/leak, under-retention/amnesia (§3 #3 #5 #7).
3. Decide who judges, before seeing results — Two blind judges, a written adjudication rule, a frozen rubric; a model judge is an instrument that needs its own calibration (§3 #8).
4. Fix everything that is not the memory system — Model and version, corpus, golden set, retrieval budget, prompt template, rubric — and write them into the results sheet (§3 #8).
5. Define the arms — Stateless and flat lexical retrieval are mandatory alongside the candidate; the lexical arm was the most accurate and the cheapest in the published suite (§3 #2).
6. Run each arm and record accuracy, total cost **including construction**, and a per-item receipt — Excluding the build is how a bake-off flatters a memory system (§3 #1).
7. Rank on cost per correct answer — `memory_engineering_calc.py cost-per-correct`; watch for the NOTE that the raw cost-per-query ranking disagrees (§3 #8).
8. Report the axes no benchmark covers — Staleness, contradiction, confabulation, erasure-verification, recall-by-distance, cost per correct answer (§3 #7 #8).
9. Freeze, re-run, report the delta — Every change re-runs the whole set; every production failure becomes a permanent item; re-run the baselines too (§3 #8).

## Output
A frozen golden set with provenance and failure-mode labels, a bake-off with at least the stateless and lexical arms, cost per correct answer per arm, and the six uncovered metrics reported beside it. See [`../skills/build-memory-eval/SKILL.md`](../skills/build-memory-eval/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- Do not cite a vendor or paper leaderboard as evidence that a memory system works here — every published ranking is self- or competitor-reported (§3 #8).
- `cost-per-correct` is shared with `budget-memory-costs` and owned by neither — this side supplies accuracy, that side supplies cost (§3 #8).
- Report the configuration with every number; a result stripped of its model, corpus, budget and query count is an anecdote.
- No user data / memory-store contents in the set, the receipts or the write-up; end with owner / date / expected movement on each recommendation.
