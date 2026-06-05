# Gate progressive rollout stages on observable metrics, not time

**Status:** Pattern
**Domain:** Feature flags / progressive rollout
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

A progressive rollout that advances by schedule ("go to 10% on Monday, 50% on
Wednesday, 100% on Friday") without a metric gate is just delayed deployment
with extra ceremony. The purpose of a progressive rollout is to detect problems
early at low blast radius before they reach full traffic. That detection requires
an observable signal — an error rate, a latency percentile, a conversion rate —
to stay within a defined envelope before the next stage triggers. A time-gated
rollout catches bugs only if the engineer happens to be watching dashboards during
the window; a metric-gated rollout is self-enforcing.

## How to apply

Define rollout stages with explicit metric gates:

```yaml
# rollout-plan/new-checkout-flow.yaml
stages:
  - traffic_pct: 1
    duration: "24h"
    gate:
      metric: checkout_error_rate
      comparison: less_than
      threshold: 0.02  # 2% error rate maximum
      window: "1h"
  - traffic_pct: 10
    duration: "48h"
    gate:
      metric: checkout_completion_rate
      comparison: greater_than
      threshold: 0.78  # Must not regress below 78%
      window: "4h"
  - traffic_pct: 50
    duration: "48h"
    gate:
      metric: checkout_completion_rate
      comparison: greater_than
      threshold: 0.78
      window: "8h"
  - traffic_pct: 100
```

Implement the gate check as an automated step in the rollout pipeline (many
flag platforms support this natively `[verify-at-use]`). The kill switch is
the fallback: if a gate check fails, the rollout pauses and the flag rolls
back automatically.

**Do:**
- Define metric gates before starting the rollout, not after you see problems.
- Include at least one error-rate or reliability gate alongside any business
  metric gate.
- Alert the on-call engineer on a gate failure, not just log it.

**Don't:**
- Advance rollout stages manually without running the metric gate check.
- Set gates only on conversion metrics and ignore error rates — a treatment
  that improves conversion at the cost of reliability is not a win.
- Use a gate window shorter than one full traffic cycle (e.g. < 1 hour for
  hourly-cycled traffic) — the window must be wide enough to be statistically
  meaningful.

## Edge cases / when the rule does NOT apply

- Hotfix deployments where speed to 100% is the safety goal (a critical bug fix):
  skip staged rollout and deploy to 100% immediately with a kill switch ready.
- Internal/beta-only flags where the entire audience is < 100 users:
  a single stage at 100% of the beta audience is fine.

## See also

- [`../agents/feature-flag-engineer.md`](../agents/feature-flag-engineer.md) — owns rollout design
- [`./every-flag-has-a-kill-switch-and-a-lifecycle.md`](./every-flag-has-a-kill-switch-and-a-lifecycle.md) — the kill switch is the fallback when a metric gate fails
- [`./separate-deploy-from-release.md`](./separate-deploy-from-release.md) — progressive rollout is the controlled release step after a dark deploy

## Provenance

Standard progressive delivery practice. Metric-gated rollout is the approach
recommended in deployment documentation for LaunchDarkly, Flagger, and Argo
Rollouts `[verify-at-use]`. The "blast radius" framing is from the site
reliability engineering literature on progressive delivery.

---

_Last reviewed: 2026-06-05 by `claude`_
