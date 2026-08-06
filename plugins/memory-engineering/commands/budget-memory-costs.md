---
description: "Put a defensible number on a memory system — break-even against a named baseline, growth and caps, cache-invalidation cost, and cost per correct answer. Reach for this on a pay-for-itself question."
argument-hint: "[the situation, e.g. the store / agent / workload in question]"
---

# Budget memory costs

You are running `/memory-engineering:budget-memory-costs` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Name the baseline — `full-context-prefill`, `lexical-retrieval` or `stateless`; it is required, has no default, and `stateless` is not the same job (§3 #1).
2. Amortize — `memory_engineering_calc.py amortize`; fold re-construction into `--build-cost` or the figure flatters the memory path (§3 #1).
3. Project growth and caps — `memory_engineering_calc.py store-growth`; with no TTL and no cap the projection is unbounded, and that is the finding (§3 #3).
4. Price the cache-invalidation bill — `memory_engineering_calc.py cache-economics`; multipliers are inputs read from the surfaces file, never defaults (§3 #1).
5. Compute cost per correct answer — `memory_engineering_calc.py cost-per-correct`; it needs an accuracy number, which means a golden set from `build-memory-eval` (§3 #8).
6. Name the costs the calculator cannot see — Build wall-clock, the bill every context-shrinking mechanism moves elsewhere, and the concurrency headroom a smaller prompt buys (§3 #1).

## Output
A break-even against a named baseline, a growth projection with the cap day, a cache-invalidation delta, and a cost per correct answer paired with the accuracy source that produced it. See [`../skills/budget-memory-costs/SKILL.md`](../skills/budget-memory-costs/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- `cost-per-correct` is shared with `build-memory-eval` and owned by neither — this side supplies cost, that side supplies accuracy (§3 #8).
- The calculator ships zero vendor constants; read every price, multiplier and cap from [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) with its date, and never present an output as a quoted price.
- No user data / memory-store contents in the output; end with owner / date / expected movement on each recommendation.
