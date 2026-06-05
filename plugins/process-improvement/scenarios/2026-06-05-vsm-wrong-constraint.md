---
scenario_id: 2026-06-05-vsm-wrong-constraint
contributed_at: 2026-06-05
plugin: process-improvement
product: lean-vsm
scope: likely-general
tags: [vsm, constraint, bottleneck, lead-time, theory-of-constraints]
confidence: medium
reviewed: false
---

## Problem

A software-delivery org wanted to cut feature lead time. They had invested heavily in speeding up the **coding** step (more developers, better tooling) — the most-complained-about, most-visible step — but end-to-end lead time barely moved. The ask: "we made the slow part faster; why isn't the whole thing faster?"

## Context

- Sector: software / internal IT delivery; "lead time" = idea accepted → in production.
- Constraint: the team had optimized the step that was *loudest*, not the step that was the *system constraint*; no end-to-end value-stream map existed — only a coarse sense that "dev is slow."
- Politically, "add developers" was the easy sell; the actual constraint sat in a less-visible, cross-team function.

## Attempts

- Tried: built a full **value-stream map** from customer trigger (idea accepted) to delivered outcome (in production) — not a slice. Captured process time *and* wait/queue time at each step. Outcome: the dominant lead-time component was **queue time waiting for a shared QA/release-approval gate**, not coding time. Coding was ~15% of lead time; the release-approval queue was ~50%. `[ESTIMATE]` proportions, illustrative.
- Tried: applied the constraint principle (Theory of Constraints / the *Waiting* leaf of the Lean-countermeasure tree). Speeding a **non-constraint** (coding) cannot speed the system — work just piles up faster in front of the real bottleneck (the release queue). Outcome: identified the genuine constraint with data, not opinion.
- Tried (the move that worked): attacked the release-approval queue — batched-to-single-piece flow, an authority push-down so routine releases didn't wait for a weekly board, and WIP caps upstream so the queue stopped growing. Outcome: end-to-end lead time dropped materially; the *re-found* constraint then moved to a different step (as it always does), and the team re-mapped.

## Resolution

The org had optimized a **sub-process, not the system**. Speeding a non-bottleneck step improves a local metric while the end-to-end number sits still — because the constraint, the release queue, was untouched. Lead time is governed by the constraint plus the queues, which only a *whole-stream* map reveals.

**Action for the next analyst hitting this pattern:** for any lead-time/throughput goal, **map the whole value stream** (customer trigger → delivered outcome), capture **wait/queue time** (usually the dominant component, and invisible on a slice-level swimlane), find the constraint with data, and direct effort *there* — then re-find it, because the constraint moves. Cross-reference [`../best-practices/optimize-the-constraint-not-a-sub-process.md`](../best-practices/optimize-the-constraint-not-a-sub-process.md) and [`../best-practices/value-stream-map-the-whole-not-a-slice.md`](../best-practices/value-stream-map-the-whole-not-a-slice.md), and the *Waiting* leaf of the Lean-countermeasure tree in [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md). Resist the loudest-step / easiest-sell instinct.

**Sources for facts cited:** the constraint and whole-stream-mapping principles are this plugin's best-practices (linked above) and the Lean-countermeasure decision tree; grounded in Theory of Constraints and Lean value-stream-mapping practice ([Lean Enterprise Institute](https://www.lean.org/)). Figures are illustrative `[ESTIMATE]`; validate against the org's actual value-stream data.
