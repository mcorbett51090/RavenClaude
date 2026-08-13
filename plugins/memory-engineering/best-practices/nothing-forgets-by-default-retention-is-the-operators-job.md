# Nothing forgets by default — retention is the operator's job.

**Status:** Absolute rule. **Constitution:** §3 #3, §4.

## Use when

Before a store takes its **first** write — and whenever anyone describes growth as "we'll deal with it later."

## The rule

**No evaluated memory system prunes or forgets by default; footprint grows monotonically under default behaviour.** Bounding it requires an independent forgetting policy that you write and own. Before the first write, state four things: **who deletes, on what trigger, at what cap, and what happens *at* the cap.**

An unbounded store is a decision that was never made.

## Why it matters

Footprint spread roughly ninefold across paradigms at 1M tokens — and bytes are the tame axis. **Token cost diverges far more sharply, super-linearly for the agentic paradigms**, because each ingestion queries the growing store before it writes. So the number that matters is the growth *slope*, not the day-one footprint, and a design reviewed on footprint alone passes review and fails in production.

The failure modes at a cap are not interchangeable, which is why "what happens at the cap" is a separate question from "what is the cap." One platform's store makes new writes **fail** at its memory-count cap; a session-startup index budget makes the overflow **silently disappear at load**. Same word, opposite incident. The current caps are dated in [memory surfaces](../knowledge/memory-surfaces-2026.md) `[verify-at-use]`.

## How to apply

- Project growth with [`store-growth`](../scripts/memory_engineering_calc.py): footprint at 30 / 90 / 365 days, and the calendar day a supplied cap is reached. Every run with no TTL and no cap prints the fixed note that nothing forgets by default — that note is the point, not noise.
- Pick the forgetting mechanism deliberately: **TTL, size cap, decay/recency scoring, explicit deletion, consolidation-with-replacement, or contradiction resolution.** They are not substitutes; most designs need two.
- Decide **when** consolidation runs — on the write path (a latency and cost tax on every turn), as an offline batch (staleness between runs), or never — and write down which bill you chose.
- Name a **retention owner** by role, not by team. A policy with no owner is a wish.
- Carry the answer into the [memory design record](../templates/memory-design-record.md) and the growth row of the [cost sheet](../templates/memory-cost-sheet.md).

## The anti-pattern this prevents

The §4 failure mode: **a store with no TTL, no cap, and no retention owner** — usually shipped because the library did not force the question and nothing broke on day one.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) §3 #3 — the house opinion this rule encodes.
- [`../knowledge/memory-engineering-economics.md`](../knowledge/memory-engineering-economics.md) — the growth model and why a cap is not a retention policy.
- [`../knowledge/memory-surfaces-2026.md`](../knowledge/memory-surfaces-2026.md) — the dated caps and what each surface does when one is reached.
- [`../agents/memory-retention-and-erasure-engineer.md`](../agents/memory-retention-and-erasure-engineer.md) — the agent that owns retention and erasure.
