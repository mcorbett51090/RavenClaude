---
name: devex-measurement
description: "Measure developer experience and platform adoption: pick the framework (DORA for delivery, SPACE for breadth, DevEx/DXI for felt friction), ship a balanced gaming-resistant metric set (1 delivery + 1 perception + 1 adoption), instrument time-to-first-PR / time-to-prod and the adoption funnel, design a low-burden developer survey, and turn the numbers into a platform backlog. Never measure individuals."
---

# DevEx Measurement

**Purpose:** measure the *system's* developer experience and platform adoption, and turn the numbers
into platform-backlog decisions.

## Choose the framework

Traverse the metric-framework tree in
[`../../knowledge/platform-engineering-decision-trees.md`](../../knowledge/platform-engineering-decision-trees.md):

- **DORA** — deploy frequency, lead time, change-fail rate, MTTR (delivery throughput & stability).
- **SPACE** — satisfaction, performance, activity, communication, efficiency (the multidimensional
  picture; pick 2-3 dimensions, not all five).
- **DevEx / DXI** — feedback loops, cognitive load, flow state (felt friction; needs a survey).

## Ship a balanced set

Always combine **1 delivery metric + 1 perception metric + 1 adoption metric** so no single proxy
gets gamed (deploy frequency alone invites tiny pointless deploys; pair it with change-fail rate and a
survey signal).

## Adoption as a funnel

`discover -> try -> adopt -> retain`. Track template runs, golden-path usage share, catalog coverage,
and retention — not a single "adoption %".

## Surveys

Low-burden, balanced, recurring; **paired with system metrics**. Perception is data — "provisioning a
DB is painful" is actionable even with no system metric behind it.

## The hard rule

**Measure the system, never the individual.** No individual-productivity leaderboards — they destroy
trust and the signal. Every metric must have a decision attached; a dashboard nobody acts on is waste.

## Output

A framework + balanced starter set, an instrumentation/dashboard plan (with each signal's source), or
a data-driven adoption diagnosis -> the 2-3 highest-leverage backlog items. Underlying telemetry ->
`observability-sre`; turning it into roadmap -> `platform-product-lead`; survey validity ->
`applied-statistics`.
