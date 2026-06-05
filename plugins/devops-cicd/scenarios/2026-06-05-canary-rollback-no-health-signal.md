---
scenario_id: 2026-06-05-canary-rollback-no-health-signal
contributed_at: 2026-06-05
plugin: devops-cicd
product: argo-rollouts
product_version: "unknown"
scope: likely-general
tags: [canary, rollback, slo, health-gate, progressive-delivery]
confidence: medium
reviewed: false
---

## Problem

A team set up a canary rollout (1% → 10% → 50% → 100% on a timer) and shipped a release that introduced a latency regression. The canary "promoted" through every stage on schedule and reached 100% — because the promotion gate was **a wall-clock timer, not a health signal**. The bad version was fully rolled out before anyone noticed; the rollback was a manual, frantic `kubectl` re-deploy of the previous tag at 1am. The ask afterward was "make the canary actually catch a bad release."

## Context

- Kubernetes with a progressive-delivery controller doing weighted traffic shifts.
- Constraint: there was **no automated analysis** wired to the canary — the steps had `pause: {duration: 5m}` between weight increases, so the rollout marched forward on time regardless of how the canary was actually behaving. A timer promotes a healthy and an unhealthy canary identically.
- The team _had_ the telemetry (p99 latency, error rate in their metrics backend) — it just wasn't connected to the rollout's promote/abort decision. The signal existed; the gate didn't read it.

## Attempts

- Tried: shortening the timer and adding more manual eyes during deploys. This is just "watch it harder" — it doesn't scale, it fails at 1am, and it's exactly what automation is for. Rejected.
- Tried: traversing the **deploy/rollout strategy** decision tree in [`../knowledge/devops-cicd-decision-trees.md`](../knowledge/devops-cicd-decision-trees.md) and [`../knowledge/deployment-strategy-and-runner-cache-decision-trees.md`](../knowledge/deployment-strategy-and-runner-cache-decision-trees.md). The tree's canary leaf is explicit: a canary needs an **SLO/burn-rate health signal** to promote/abort on — _without_ that signal you do not have a canary, you have a slow timed rollout. The promote/abort signal is owned by `observability-sre`; the canary is only as good as the gate it reads.
- Tried (the move that worked): wired **automated analysis** — the rollout now queries the metrics backend at each step (success-rate and p99 thresholds) and **aborts + auto-rolls-back** when the canary breaches the gate, instead of advancing on a timer. Re-shipped the regression in a game-day: the canary breached the p99 threshold at the 10% step and auto-rolled-back in under two minutes, no human in the loop, no 1am page.

## Resolution

**A canary that promotes on a timer is not a canary — it's a slow uniform rollout that still ships a bad version, just more gradually.** The whole value of a canary is the automated promote/abort decision, and that decision is only as good as the health signal feeding it. The fix was not a faster timer or more human attention; it was connecting the SLO signal the team already collected to the rollout's gate so the abort path runs automatically.

**Action for the next engineer:** before calling a rollout a "canary," confirm it has a real health signal wired to its promote/abort gate (success rate, error budget burn, p99 latency) — a `pause: {duration}` between weight steps is a timer, not a gate. The signal definition belongs to `observability-sre`; if there is no signal yet, the honest strategy is "rolling + manual gate, and add a health signal next" (a decision-tree leaf), not a canary that can't see. Decide the rollback path _before_ you ship — automated abort beats a heroic 1am re-deploy (§3 #2). Cross-reference [`../best-practices/deploy-rollback-before-you-ship.md`](../best-practices/deploy-rollback-before-you-ship.md) and [`../templates/canary-rollout-plan.md`](../templates/canary-rollout-plan.md).

**Sources:** weighted-canary + automated-analysis promote/abort is the documented Argo Rollouts model — confirm the current `AnalysisTemplate` / metric-provider mechanism against the [Argo Rollouts docs](https://argo-rollouts.readthedocs.io/) at use `[verify-at-use]`; Flux/Flagger offers the same pattern. Timings/thresholds are illustrative; the SLO and its thresholds are the consuming team's (and `observability-sre`'s) to set.
