# Memory cost lives on the write path — amortize before you adopt.

**Status:** Absolute rule. **Constitution:** §3 #1, §4.

## Use when

Anyone proposes adding, expanding, or keeping a durable agent memory store — and at every point where a design decision changes how often something is **written**.

## The rule

Price the **write path** before the read path, and do not adopt a memory system until you have computed its break-even against a **named** baseline. For LLM-mediated systems the benchmark's construction energy exceeded *all* of its query-phase energy across its 300 queries — and 300 is that benchmark's fixed query count, **not** a measured crossover point. No published break-even exists, which is exactly why you compute your own.

Folded into the same rule: **a design that invalidates the prompt cache once per turn pays the re-warm multiple instead of the cheap cached read.** A write that lands *ahead* of the reused prefix invalidates everything after it. Append memory at the end of the prompt, or pay that bill every turn.

## Why it matters

Every accuracy benchmark in the field measures the read path and is structurally blind to the write path, so the cost that actually decides the project is the one nobody publishes. Construction wall-clock on one corpus ran from minutes for a lexical index to hours for a consolidating store and longer still for a fully agentic one — and the agentic family is the only one whose cost slope is super-linear, because each ingestion reads the growing store before writing to it. A proposal that quotes retrieval quality and stops has not priced the thing it is asking you to buy.

## How to apply

- **Name the baseline first**, then compute. [`amortize`](../scripts/memory_engineering_calc.py) requires `--baseline` and has no default: `full-context-prefill` and `lexical-retrieval` do the same job; `stateless` does **not**, and the tool says so before it prints a number.
- Run `amortize --build-cost … --per-query-cost-with … --per-query-cost-without … --baseline …`. If the denominator is ≤ 0 there is no break-even at all — the only argument left for the system is accuracy, so switch to `cost-per-correct`.
- Price the cache separately with `cache-economics`. Supply the **current** published multipliers yourself; they are dated in [memory surfaces](../knowledge/memory-surfaces-2026.md) `[verify-at-use]` and deliberately not baked into the script.
- Count the mechanisms that make context smaller: each one bills somewhere else. Free compression does not exist — see [memory economics](../knowledge/memory-engineering-economics.md).
- Put the break-even query volume, the named baseline, and the cache bill in the [memory design record](../templates/memory-design-record.md) and the [cost sheet](../templates/memory-cost-sheet.md). A break-even with no baseline beside it is not a number.

## The anti-pattern this prevents

The §4 failure mode: **adopting a memory system without amortizing its write path against a named baseline** — a proposal that reports what the store retrieves and never what it cost to fill. The plugin's advisory hook flags a deliverable that makes a cost or break-even claim with no baseline named anywhere in it.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #1 — the house opinion this rule encodes.
- [`../knowledge/memory-engineering-economics.md`](../knowledge/memory-engineering-economics.md) — the four formulas, the worked example, and the exit-code contract.
- [`../agents/memory-eval-cost-analyst.md`](../agents/memory-eval-cost-analyst.md) — the agent that owns the calculator and this rule.
