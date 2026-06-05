---
scenario_id: 2026-06-05-tutorial-reference-confusion
contributed_at: 2026-06-05
plugin: technical-writing-docs
product: diataxis
product_version: "unknown"
scope: likely-general
tags: [diataxis, tutorial, reference, content-type, time-to-first-success]
confidence: medium
reviewed: false
---

## Problem

A library's "Getting Started" tutorial had a 70%+ drop-off before the first working example. The page opened with a complete configuration reference — every option, every default, a table of all 24 environment variables — *before* the reader had run anything. New users bounced; experienced users complained the same page buried the config table they wanted to look up under a beginner walkthrough. One page was trying to be both a tutorial and a reference, and it failed at both: it neither got a beginner to first success quickly nor let an expert look up a fact fast.

## Constraints context

- The team conflated "Getting Started" (a Diátaxis **tutorial** — a guided, guaranteed-to-succeed first experience) with "everything you need to know to start" (which is reference). The label hid the kind-confusion.
- A tutorial's job is **time-to-first-success**: one happy path, no choices, no exhaustive options. The config table is reference — look-up material the learner does not need yet (`optimize-time-to-first-success`, `scope-the-tutorial-to-one-success`).
- Pressure to "be complete" pushed reference content into the learning path — the single most common Diátaxis failure mode.

## Attempts

- Tried: shortening the config table on the tutorial page. Didn't fix it — a shorter reference table in a tutorial is still reference in a tutorial. The kind was wrong, not the length.
- Tried: adding a "skip to the example" anchor at the top. A band-aid — the page still served two masters; the anchor admitted the structure was wrong.
- Tried (the move that worked): **split the page by Diátaxis kind**. A tutorial scoped to exactly one guaranteed success (install → one minimal working call → "you did it"), with zero configuration choices, every value hardcoded; and a separate **Configuration reference** page owning the 24-variable table. The tutorial links to the reference at the end ("now that it works, here's how to configure it"). Traversed `knowledge/technical-writing-docs-decision-trees.md` "Which kind of doc is this (Diataxis)?" and the new content-type tree.

## Resolution

The fix was to **stop mixing two Diátaxis kinds on one page**. A tutorial optimizes for first success (one path, no choices); reference optimizes for look-up (complete, accurate, scannable). Splitting them let the tutorial cut drop-off and let the reference table become findable for the experts who wanted it. The litmus: if a page makes a beginner choose between options before their first success, the options belong in reference, not the tutorial.

**Action for the next writer hitting a high-drop-off "Getting Started":** ask which Diátaxis kind it *is* before editing the prose. If it contains a complete options/config table, it is two kinds wearing one title — split it. The tutorial keeps exactly one happy path to one success with every value hardcoded; the reference owns completeness. Canonical guidance: [`../knowledge/diataxis-content-type-selection-decision-tree.md`](../knowledge/diataxis-content-type-selection-decision-tree.md), [`../knowledge/technical-writing-docs-decision-trees.md`](../knowledge/technical-writing-docs-decision-trees.md), and the [`scope-the-tutorial-to-one-success`](../best-practices/scope-the-tutorial-to-one-success.md) + [`optimize-time-to-first-success`](../best-practices/optimize-time-to-first-success.md) + [`know-which-diataxis-kind`](../best-practices/know-which-diataxis-kind.md) best-practices.

**Sources (retrieved 2026-06-05):**
- Diátaxis — Tutorials (a tutorial is a lesson; the learner does, under guidance): https://diataxis.fr/tutorials/
- Diátaxis — "The difference between a tutorial and how-to guide": https://diataxis.fr/tutorials-how-to/
- Diátaxis — Reference: https://diataxis.fr/reference/

These are stable framework sources; the "70% drop-off" is this-engagement specific and not a benchmark — `[verify-at-use]` against the consumer's own funnel analytics.
