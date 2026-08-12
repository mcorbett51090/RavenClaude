---
description: "Decide whether to build a memory system at all, and if so which paradigm, behind a mandatory baseline-first gate. Reach for this before any memory design work."
argument-hint: "[the situation, e.g. the store / agent / workload in question]"
---

# Choose memory paradigm

You are running `/memory-engineering:choose-memory-paradigm` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Name the durable question — What must survive this session, and which later session reads it (§3 #4).
2. STOP — prove the no-memory baseline loses — Measure accuracy and cost with no injected history; if it is good enough, do not build memory (§3 #2).
3. STOP — prove flat lexical retrieval loses — BM25 or an embedding index over the same history; it was the most accurate and the cheapest system in the published suite (§3 #2).
4. Classify along the four axes — Construction, storage, retrieval, mutability — construction is where the money goes (§3 #1).
5. Name the paradigm and its bill — I raw context, II flat retrieval, III.a structure-augmented, III.b consolidating store, IV agentic (§3 #1).
6. Amortize against the baseline you beat — Hand to `budget-memory-costs`; no break-even means the case is accuracy-only (§3 #1 #8).
7. Record the decision — Paradigm, the baseline that lost, the measured gap, break-even, owner, date (§3 #4).

## Output
A paradigm decision with both baselines measured and beaten, the four-axis classification, and a break-even against a named baseline. Traverse Tree 1 in the decision-trees file. See [`../skills/choose-memory-paradigm/SKILL.md`](../skills/choose-memory-paradigm/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user data / memory-store contents in the output; cite a source + date for every external figure (or mark it).
- Never pick a paradigm from a leaderboard — every published memory ranking is self- or competitor-reported (§3 #8).
- End with owner / date / expected movement on each recommendation.
