# experimentation-growth-engineering — best-practice docs

Named, citable rules for the `experimentation-growth-engineering` plugin's specialists. Each file is **one rule**, grounded in this plugin's domain: feature flags and safe rollouts, A/B test plumbing, and trustworthy product-analytics event instrumentation.

Statistical validity (power, significance, "is the lift real") routes to `applied-statistics`. These rules cover the apparatus — assignment, exposure logging, flags, instrumentation — and the structural decisions that make the apparatus trustworthy.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`analyze-on-exposure-not-assignment.md`](./analyze-on-exposure-not-assignment.md) | Absolute rule | Setting up the analysis window for an experiment |
| [`instrumentation-is-a-designed-schema.md`](./instrumentation-is-a-designed-schema.md) | Absolute rule | Starting any analytics instrumentation work |
| [`sequential-vs-fixed-horizon.md`](./sequential-vs-fixed-horizon.md) | Pattern | Choosing the analysis regime for a new experiment |
| [`check-srm-before-trusting-a-result.md`](./check-srm-before-trusting-a-result.md) | Primary diagnostic | An experiment result is in hand and needs validation |
| [`guardrail-metrics-on-every-experiment.md`](./guardrail-metrics-on-every-experiment.md) | Absolute rule | Designing any experiment — before registering the primary metric |
| [`every-flag-has-a-kill-switch-and-a-lifecycle.md`](./every-flag-has-a-kill-switch-and-a-lifecycle.md) | Absolute rule | Creating a new feature flag |
| [`build-the-apparatus-route-significance.md`](./build-the-apparatus-route-significance.md) | Absolute rule | Any time this team is about to compute a p-value |
| [`stitch-identity-across-the-login-boundary.md`](./stitch-identity-across-the-login-boundary.md) | Absolute rule | Any product with anonymous and authenticated states |
| [`separate-deploy-from-release.md`](./separate-deploy-from-release.md) | Pattern | Shipping any user-visible feature |
| [`deterministic-assignment-server-side.md`](./deterministic-assignment-server-side.md) | Absolute rule | Implementing experiment assignment logic |
| [`one-definition-per-event.md`](./one-definition-per-event.md) | Absolute rule | Adding or auditing any analytics event |
| [`no-peeking-pre-register.md`](./no-peeking-pre-register.md) | Absolute rule | Registering an experiment before launch |
| [`flag-debt-cleanup-on-schedule.md`](./flag-debt-cleanup-on-schedule.md) | Absolute rule | Creating a new feature flag; quarterly flag audit |
| [`mutual-exclusion-for-concurrent-experiments.md`](./mutual-exclusion-for-concurrent-experiments.md) | Absolute rule | Running two or more experiments that share a surface |
| [`holdout-group-for-long-term-effects.md`](./holdout-group-for-long-term-effects.md) | Pattern | Designing the experimentation programme at a product with > 10 experiments/quarter |
| [`instrument-funnel-at-decision-points-not-page-views.md`](./instrument-funnel-at-decision-points-not-page-views.md) | Pattern | Designing conversion funnel instrumentation |
| [`server-side-assignment-to-prevent-flicker.md`](./server-side-assignment-to-prevent-flicker.md) | Pattern | Implementing experiment assignment for any frontend-rendered surface |
| [`cdp-fan-out-over-direct-integrations.md`](./cdp-fan-out-over-direct-integrations.md) | Pattern | Adding a second or subsequent analytics destination |
| [`targeting-rules-are-code-version-them.md`](./targeting-rules-are-code-version-them.md) | Pattern | Creating or changing feature flag targeting rules |
| [`anonymous-users-need-stable-ids.md`](./anonymous-users-need-stable-ids.md) | Absolute rule | Any experiment that includes non-authenticated users |
| [`metric-sensitivity-before-launch.md`](./metric-sensitivity-before-launch.md) | Primary diagnostic | Choosing the primary metric for a new experiment |
| [`event-schema-versioning.md`](./event-schema-versioning.md) | Absolute rule | Changing an existing analytics event property |
| [`progressive-rollout-requires-observable-metrics.md`](./progressive-rollout-requires-observable-metrics.md) | Pattern | Designing a progressive rollout plan for any feature flag |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution and house opinions
- [`../knowledge/experimentation-growth-engineering-decision-trees.md`](../knowledge/experimentation-growth-engineering-decision-trees.md) — decision trees the agents traverse
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs
