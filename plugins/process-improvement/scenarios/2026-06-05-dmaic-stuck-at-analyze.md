---
scenario_id: 2026-06-05-dmaic-stuck-at-analyze
contributed_at: 2026-06-05
plugin: process-improvement
product: dmaic
scope: likely-general
tags: [dmaic, analyze, root-cause, hypothesis-test, statistics-seam]
confidence: medium
reviewed: false
---

## Problem

A DMAIC on invoice-processing cycle time had a solid charter, a clean baseline (median ~9 days, wide spread), and a fishbone with a dozen candidate causes — but the team had been stuck in **Analyze for six weeks**. Every cause was "plausible"; nobody could agree which was *the* cause, and the sponsor was pushing to "just pick one and start fixing."

## Context

- Sector: shared-services finance; the metric (invoice cycle time) was well-defined and the data existed in the ERP.
- Constraint: schedule pressure from the sponsor to jump to Improve; the team was conflating *brainstormed* causes with *proven* causes.
- The team had done the divergent work (fishbone, 5-Whys) but had no convergent, data-based step to discriminate among the survivors.

## Attempts

- Tried: ran a **Pareto** on defect/delay frequency by cause category. Two categories (approval-routing wait, missing-PO rework) accounted for the bulk of the delay-days — the "vital few." Outcome: narrowed twelve candidates to two worth testing. `[ESTIMATE]` proportions, illustrative.
- Tried: recognized the actual blocker — the team was treating a **plausible** cause as a **proven** one. Per the root-cause tree, the exit from Analyze is a *proof gate*, not a vote. "Does approval-routing wait actually drive cycle time?" is an inference question. Outcome: named the gate the team had been skipping.
- Tried (the move that worked): **routed the confirmatory inference to `applied-statistics`** (the load-bearing seam, CLAUDE.md §8) — a hypothesis test on cycle time partitioned by whether the invoice hit the approval-routing wait, with effect size + CI. The black belt *named* the question in process terms; the statistician ran and defended the test. The test confirmed approval-routing as a real driver (and ruled out a third suspected cause as noise). Outcome: a **proven** root cause, Analyze gate passed, Improve began on solid ground.

## Resolution

The DMAIC was stuck because the team had no mechanism to move from *many plausible causes* to *one proven cause* — and "just pick one" would have attached the fix to a guess. The unblock was a Pareto to narrow, then **routing the proof to the statistics seam** rather than asserting causation by consensus. This plugin frames *which* question and *which* phase; `applied-statistics` answers *is it real*.

**Action for the next Black Belt hitting this pattern:** when Analyze stalls on "which cause," traverse the **which-root-cause-tool** tree in [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md): fishbone/5-Whys generate hypotheses, Pareto ranks the vital few, and the *proof gate* is a confirmatory test routed to `applied-statistics` — never exit to Improve from a fishbone alone. Resisting the sponsor's "pick one and go" is the anti-solution-jumping discipline (CLAUDE.md §4 #4). The black belt names the candidate test; the statistician runs, defends, and assumption-checks it.

**Sources for facts cited:** the fishbone→5-Whys→Pareto→confirmatory-test sequence and the proof-gate seam are documented in [`../knowledge/process-improvement-decision-trees.md`](../knowledge/process-improvement-decision-trees.md) §"Which root-cause tool?" and [`../CLAUDE.md`](../CLAUDE.md) §8. Figures are illustrative `[ESTIMATE]`; validate against the client's actual data and let `applied-statistics` certify any significance claim.
