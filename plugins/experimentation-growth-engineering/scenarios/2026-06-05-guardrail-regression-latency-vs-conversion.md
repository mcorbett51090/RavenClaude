---
scenario_id: 2026-06-05-guardrail-regression-latency-vs-conversion
contributed_at: 2026-06-05
plugin: experimentation-growth-engineering
product: experimentation
product_version: "n/a"
scope: likely-general
tags: [guardrail, latency, conversion, regression, ship-decision]
confidence: medium
reviewed: false
---

## Problem

A recommendation-widget experiment showed a clean, trustworthy, significant +3% lift on add-to-cart — a clear win on the primary metric. The team shipped it. Two weeks later, overall session-level revenue was *down* and support tickets about a "sluggish" page rose. The widget had added ~250ms to page load; the primary metric improved while a guardrail (page latency, and downstream session abandonment) silently regressed. The test wasn't wrong about add-to-cart; the team had no guardrail to catch the trade.

## Context

- Primary metric: add-to-cart rate. No latency or revenue-per-session guardrail was pre-registered on the experiment.
- The widget made an extra synchronous call that slowed the page for a slice of users.
- The lift was real and SRM-clean — this was not a trustworthiness failure; it was a *scope-of-metrics* failure.

## Attempts

- Tried: rolling back and blaming the analysis. Wrong frame — the add-to-cart result was correct. The problem was that a single primary metric can't see a cross-cutting harm.
- Tried (the move that worked): re-ran with a **guardrail-metric set pre-registered alongside the primary** — page latency (p95), errors, and revenue-per-session — with explicit non-inferiority thresholds. The re-run reproduced the +3% add-to-cart **and** showed the latency regression and a small revenue-per-session dip outside tolerance. That converted an invisible loss into an explicit, visible trade.
- Tried (the engineering fix): made the widget's extra call **asynchronous / non-blocking** so it stopped costing latency, then re-tested. With latency neutral, the add-to-cart win held and the guardrails stayed green — a genuine ship.

## Resolution

**A significant primary metric with a tripped guardrail is not a win — it's a trade the business has to make explicitly, and most of the time it means "don't ship as-is."** Every experiment carries a guardrail set (latency, errors, revenue-per-session, key downstream metrics) with pre-registered thresholds, so a primary-metric win that harms a guardrail surfaces at decision time instead of in production two weeks later.

**Action for the next engineer:** never let an experiment launch with only a primary metric. Pre-register guardrails (reliability + the business metric the primary could cannibalize) and treat a guardrail breach as blocking, not advisory. When the primary wins but a guardrail trips, the decision routes to the business as an explicit trade — and the reliability guardrails (latency/errors) are effectively never tradeable. Whether the guardrail movement is *significant* is `applied-statistics`' call; defining the guardrail set and enforcing the gate is the apparatus's (CLAUDE.md §3 #1).

Cross-reference: complements [`../best-practices/guardrail-metrics-on-every-experiment.md`](../best-practices/guardrail-metrics-on-every-experiment.md), the "Ship, iterate, or kill" and "Progressive rollout — advance, pause, or rollback?" trees in [`../knowledge/experimentation-growth-engineering-decision-trees.md`](../knowledge/experimentation-growth-engineering-decision-trees.md), and the new "Ship / iterate / kill on a guardrail breach" tree in [`../knowledge/ship-iterate-kill-guardrail-decision-tree.md`](../knowledge/ship-iterate-kill-guardrail-decision-tree.md).

**Sources (retrieved 2026-06-05):**
- Guardrail / non-inferiority metric practice in online experimentation is standard industry practice (Kohavi/Tang/Xu, *Trustworthy Online Controlled Experiments*) `[unverified — training knowledge; offered as a pointer, not a this-session citation]`. The decision logic here is grounded in the plugin's own pre-existing best-practices, not a single external source.
