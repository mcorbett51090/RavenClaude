# Every published memory ranking is self- or competitor-reported — build your own golden set.

**Status:** Pattern. **Constitution:** §3 #8, §4.

## Use when

Anyone reaches for a vendor benchmark, a paper's headline table, or a leaderboard as evidence that a memory system will work **here**.

## The rule

**Do not cite a published memory-system ranking as evidence.** Every one of them is self-reported by its vendor or reported by a competitor, and a public head-to-head by a neutral party was not located. Build a golden set on your own data and measure **cost per correct answer**.

`cost-per-correct` is the falsifiability metric because **accuracy without cost and cost without accuracy are both unfalsifiable.** It is shared between the cost lane and the eval lane and owned by neither: one supplies the cost, the other supplies the accuracy, and neither number means anything alone.

## Why it matters

The disclosure asymmetry is the whole problem: a vendor publishes the axis it wins on. Numbers circulate as properties of the technique when they are properties of one customer's deployment — two customers' unaudited testimonials get generalized into an expected outcome, and the expected outcome ends up in a slide that a budget is approved against. Attribute a testimonial or drop it; never present one as an expected outcome.

The benchmark layer is contested too, not merely thin: conversations in the most-cited multi-session set fit comfortably inside a modern context window, so a no-memory long-context baseline is a live contender on the very benchmark used to justify memory.

> If a benchmark later covers staleness and contradiction handling directly — Locomo-Plus (arXiv 2602.10715) is the nearest candidate and is not primary-read here — cite it and narrow this opinion to the cost axis; the self-reporting problem survives either way.

## How to apply

- Build a **golden set with provenance**: where each item came from, who judged it, and when. A golden set nobody can trace is a vendor benchmark with your logo on it.
- Judge the **failure modes**, not just correctness: stale fact, unresolved contradiction, confabulated recall, poisoned recall, over-retention (it should have forgotten) and amnesia (it should have remembered). Aggregate accuracy hides all six.
- Report **cost per correct answer** for every system in the bake-off, computed with the [calculator](../scripts/memory_engineering_calc.py), and name the baseline it is measured against.
- Give every external figure a **source URL and a retrieval date**, or mark it `[unverified — training knowledge]`. Volatile vendor facts carry `[verify-at-use]`.
- Record the run in the [eval sheet](../templates/memory-eval-sheet.md); a bake-off with no recorded inputs is not reproducible and therefore is not evidence.

## The anti-pattern this prevents

The §4 failure mode: **quoting a vendor or paper leaderboard as evidence that a memory system works here** — and its cousin, an external benchmark number with no source URL and no retrieval date. The plugin's advisory hook flags a deliverable that carries a benchmark figure with no citation and no `[unverified]` marker.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #8 — the house opinion this rule encodes.
- [`../knowledge/memory-engineering-paradigms.md`](../knowledge/memory-engineering-paradigms.md) — the landscape, the contested benchmarks, and why no leaderboard is worth citing.
- [`../knowledge/memory-engineering-economics.md`](../knowledge/memory-engineering-economics.md) — the cost half of the shared metric.
- [`../agents/memory-eval-cost-analyst.md`](../agents/memory-eval-cost-analyst.md) — the agent that runs the bake-off.
