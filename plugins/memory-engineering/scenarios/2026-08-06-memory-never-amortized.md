---
scenario_id: 2026-08-06-memory-never-amortized
contributed_at: 2026-08-06
plugin: memory-engineering
product: memory-economics
product_version: "n/a"
scope: likely-general
tags: [amortization, baseline, write-path, cost-per-correct, lexical-retrieval, cache]
confidence: medium
reviewed: false
---

## Problem

A team replaced a keyword index with an LLM-mediated fact store because retrieval "felt smarter." Six weeks in, spend was up and the answer quality complaints had not moved. Asked when the rebuild paid for itself, nobody could answer — the proposal had compared the new store against *the old store's roadmap*, never against a baseline. The risk: memory cost lives on the write path, and adopting without amortizing against a named baseline is a build cost with no return (§3 #1, #2).

## Context

- Every ingested event triggered an extraction call before anything was ever read back.
- Constraint: the proposal reported retrieval quality and nothing about construction (§3 #1).
- The prompt was assembled with the memory block ahead of the stable instructions.
- No golden set existed, so "quality" was a stand-up opinion.

## Attempts

- Tried: **naming the baseline and running the arithmetic** (`memory_engineering_calc.py amortize --baseline lexical-retrieval`). Outcome: the per-query delta against the lexical baseline was slightly *negative* — the denominator was ≤ 0 and the run printed the labelled no-break-even branch. There was no break-even to find, at any volume (§3 #1).
- Tried: **`--baseline stateless` to make the number look better.** Outcome: the tool printed its functional-non-equivalence warning **before** the figure — a stateless system cannot answer memory-dependent queries, so the comparison was not the same job and the number was arithmetically correct and analytically worthless.
- Tried: **`cost-per-correct` on a hastily built golden set**, since accuracy was the only argument left. Outcome: the lexical baseline won on both axes — cheaper *and* more correct — which mirrors the humbling result in [the paradigms file](../knowledge/memory-engineering-paradigms.md) (§3 #2).
- Tried: **`cache-economics` with the current published multipliers supplied at run time.** Outcome: the memory block sat ahead of the reused prefix, so nearly every turn re-warmed the whole prefix instead of reading it. Moving the block to the end of the prompt removed a recurring bill nobody had attributed to the memory system (§3 #1).

## Resolution

The fix was to **keep the lexical index, delete the extraction pipeline, and move the remaining memory block to the end of the prompt** — not to tune the store. The output was a [cost sheet](../templates/memory-cost-sheet.md) with a named baseline, the no-break-even finding stated plainly, the cache delta, and a [design record](../templates/memory-design-record.md) whose alternatives section finally had the two baselines in it.

**Action for the next engineer hitting this pattern:** **compute the break-even before you adopt, against a baseline you name out loud.** If the denominator is ≤ 0 there is no break-even and the only remaining argument is accuracy — so go measure accuracy and cost together, on your own data. Prove the no-memory and lexical baselines lose first; they very often do not. See [memory economics](../knowledge/memory-engineering-economics.md) and the `amortize` and `cost-per-correct` modes of [the calculator](../scripts/memory_engineering_calc.py).

Figures in this narrative are illustrative and unverified — treat as `[unverified — training knowledge]`, and re-check every published cache multiplier and cap `[verify-at-use]` against [memory surfaces](../knowledge/memory-surfaces-2026.md) before any deliverable (§3 #8).
