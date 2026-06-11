---
scenario_id: 2026-06-11-vanity-metrics-hid-an-activation-leak
contributed_at: 2026-06-11
plugin: developer-relations
product: devrel-metrics
product_version: "n/a"
scope: likely-general
tags: [vanity-metrics, activation, scorecard, attribution]
confidence: medium
reviewed: false
---

## Problem

A DevRel team reported a quarter of record GitHub stars and follower growth, and the exec team was
pleased — until the CFO asked why revenue from self-serve developers was flat. The risk: stars and
followers are inputs that rise without the product getting any better, and they were masking a falling
activation rate underneath.

## Context

- Surface: the quarterly DevRel scorecard, led by stars/followers/impressions.
- Constraint: the only outcome that funds self-serve is developers reaching value (activation →
  adoption), and that number was not on the scorecard.
- The team reasoned from the metrics that were easy to grow, not the ones that mattered.

## Attempts

- Tried: **instrumented the activation funnel** (sign_up → credential → first_call → first_success)
  via `devrel_calc.py funnel_conversion`. Outcome: activation rate had dropped from 31% to 22% over
  the same quarter the stars rose.
- Tried: **paired every vanity input with its outcome** on a two-column scorecard. Outcome: the
  "record growth" story collapsed — reach was up, activation was down, and the gap was the whole story.
- Tried: **traced the drop** to a credential→first_call leak introduced by an SDK version bump.
  Outcome: a specific, fixable onboarding regression, not a marketing problem.

## Resolution

The fix was to **rebuild the scorecard as outcomes-first (activation, TTFV, cost-per-activation) with
vanity inputs only ever shown paired** — and to route the real leak to the DX engineer. The output
was the two-column scorecard, the activation-drop diagnosis, and the SDK regression to fix.

**Action for the next consultant hitting this pattern:** **never report a vanity number without the
activation number behind it.** When a stars/followers line is up, pull the activation funnel before
celebrating — the two routinely move in opposite directions. See `best-practices/measure-activation-not-vanity.md`
and `knowledge/devrel-metrics-and-roi-reference.md`.

Attribution is imperfect for developers — state the assumption rather than over-claim
(`[unverified — confirm against the team's instrumentation]`).
