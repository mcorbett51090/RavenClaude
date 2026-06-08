---
scenario_id: 2026-06-08-vanity-platform-metrics
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: generic
product_version: "unknown"
scope: likely-general
tags: [devex, dora, space, vanity-metrics, adoption-funnel]
confidence: high
reviewed: false
---

## Problem

A platform team's quarterly review led with "we shipped 23 platform features and increased deploy
frequency 40%." Leadership was pleased; the stream-aligned teams were not — their lived experience was
that shipping still felt slow and painful. The platform lead wanted a metric set that would tell the
truth instead of flattering the team, and resisted a request from a director to start tracking
"commits per developer" to "find the low performers."

## Context

- The headline metrics were pure output (features shipped) and a single gameable proxy (deploy
  frequency), which had risen partly because teams were splitting changes into tiny deploys to look
  active.
- There was no perception signal at all — no developer survey — so "it feels slow" had no data behind
  it and was dismissed.
- The director's "commits per developer" request threatened to turn DevEx data into individual
  surveillance.

## Attempts

- Refused: the individual-productivity tracking, per **never-measure-individual-developers** — it would
  collapse trust and corrupt the signal, and commits-per-dev measures nothing real.
- Tried: replacing the vanity set with a **balanced** set per **measure-outcomes-not-output** — one
  delivery metric (lead time *and* change-fail rate together, so tiny-deploy gaming shows up as
  instability), one perception metric (a quarterly DevEx survey), and one adoption metric (golden-path
  usage share via the funnel).
- Tried (the move that worked): attached a **decision** to each metric and reported at team/cohort
  granularity only. The survey immediately surfaced the real top friction (a 20-minute local build),
  which became the next backlog item — something "features shipped" had never revealed.

## Resolution

**A platform team's KPI is someone else's velocity and experience, not its own output — and the moment
a DevEx metric names an individual, it stops being useful.** Swapping the vanity set for a balanced,
system-level set (delivery + perception + adoption, each with a decision attached) turned the metrics
from a flattering story into a backlog generator, and refusing individual tracking preserved the trust
the survey depended on.

**Action for the next engineer:** lead with outcomes, balance the set so single proxies can't be
gamed, pair every system metric with a perception signal, and never attribute DevEx metrics to
individuals. Cross-reference [`../best-practices/measure-outcomes-not-output.md`](../best-practices/measure-outcomes-not-output.md)
and [`../best-practices/never-measure-individual-developers.md`](../best-practices/never-measure-individual-developers.md).

**Sources:** DORA + SPACE + DevEx (DXI) guidance `[verify-at-use]`. Figures (23 features, 40%, 20-min
build) are illustrative; validate against the org's actuals.
