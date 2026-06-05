---
scenario_id: 2026-06-05-realization-rate-recovery
contributed_at: 2026-06-05
plugin: legal-small-firm
product: finance
product_version: "n/a"
scope: likely-general
tags: [realization, write-down, billing-cadence, effective-rate, collections]
confidence: medium
reviewed: false
---

## Problem

A 3-attorney litigation-and-transactional firm was "busy but broke" — high billed hours, but the bank balance never tracked the apparent workload. The owner had been raising standard rates to fix it, and realization kept *falling*. The risk: chasing the rate when the leak is downstream (write-downs at billing, write-offs at collection, and aged A/R) burns client goodwill on a rate increase that the realization cascade quietly eats anyway.

## Context

- Segment: small-business + litigation mix, independent, 3 attorneys + 1 paralegal, hourly-dominant book.
- Constraint: the firm tracked **billed hours** as its master number — which is fiction until collected (§3 #1). It had no view of the **realization cascade** (utilization → realization → collection) or the **effective hourly rate** (collected revenue ÷ hours worked), so it couldn't see *where* in the cascade the money leaked.
- Industry frame for calibration (not the firm's own data): Clio's 2025 Legal Trends pegs the averages at **~38% utilization, ~88% realization, ~93% collection** — so the typical lawyer banks only ~2.4 of 8 hours. A firm that looks "fully billed" can still be leaking at every stage. `[verify-at-use]` — these are aggregate benchmarks, not this firm's truth.

## Attempts

- Tried: built the **realization waterfall** before touching the rate — standard value (hours worked × standard rate) → billed value (after pre-bill write-downs) → collected value (after write-offs + discounts), with the gap at each step. Outcome: located the leak. Most of the loss was a **write-down at billing** (vague time entries the owner discounted himself to avoid client pushback), not a rate problem and not a collection problem.
- Tried: traced the write-downs by segment and matter type per the billing-rate-review decision tree. Outcome: the loss concentrated in one matter type with open-ended scope — a **scoping/fee-structure** problem in that segment, not a blended-rate problem. A rate increase would not have touched it.
- Tried (the move that worked): fixed **billing cadence and description quality** (contemporaneous time capture, defensible narratives) and put the open-ended segment on an hourly-with-budget structure with a re-scope trigger. Held the standard rate flat. Outcome: billed realization recovered because fewer hours were discounted away at the pre-bill, and the effective hourly rate rose without a rate change.

## Resolution

The leak was a **write-down at billing driven by weak time narratives + un-scoped matters**, not the standard rate. The fix was billing-cadence discipline and a fee-structure change in one segment, holding the rate flat — realization is the practice's truth, and the rate is rarely the lever (§3 #1, #4).

**Action for the next consultant hitting this pattern:** build the realization waterfall **before** recommending any rate change. Read whether the loss is a write-down (billing-description / cadence), a write-off (collections / scope), or aged A/R — each has a different fix, and the rate is the lever in only one of them (stale rates + market supports an increase). The [`../scripts/legal_calc.py`](../scripts/legal_calc.py) `realization` mode computes the full cascade and the effective hourly rate; the [`../knowledge/legal-practice-decision-trees.md`](../knowledge/legal-practice-decision-trees.md) "Billing Rate Review" tree routes the diagnosis.

**Sources (retrieved 2026-06-05):**
- Clio — 2025 Legal Trends benchmarks (utilization 38% / realization 88% / collection 93%): https://www.clio.com/resources/legal-trends/benchmarks/
- Clio — Highlights From the 2025 Legal Trends for Solo and Small Law Firms: https://www.clio.com/blog/solo-small-law-firms-highlights-2025-legal-trends/

Benchmarks are aggregate and move year to year — treat as `[verify-at-use]` and calibrate to the firm's own waterfall and segment, never substitute the benchmark for the firm's actual numbers (§3 #8).
