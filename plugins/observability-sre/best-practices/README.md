# observability-sre — best-practice docs

Named, citable rules for the `observability-sre` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules._

| Doc | Status | Use when |
|---|---|---|
| [`alert-on-symptoms-not-causes.md`](./alert-on-symptoms-not-causes.md) | Absolute rule | Writing or reviewing any alert |
| [`measure-the-four-golden-signals.md`](./measure-the-four-golden-signals.md) | Absolute rule | Designing service observability |
| [`set-an-explicit-cardinality-budget.md`](./set-an-explicit-cardinality-budget.md) | Absolute rule | Adding a new metric or label |
| [`measure-toil-then-budget-it-down.md`](./measure-toil-then-budget-it-down.md) | Pattern | Planning the SRE team's reliability work |
| [`every-page-is-actionable.md`](./every-page-is-actionable.md) | Absolute rule | Reviewing the on-call alert roster |
| [`postmortems-are-blameless.md`](./postmortems-are-blameless.md) | Absolute rule | Running or reviewing a postmortem |
| [`one-runbook-per-alert.md`](./one-runbook-per-alert.md) | Absolute rule | Creating or updating an alert |
| [`choose-tail-sampling-for-the-rare-and-bad.md`](./choose-tail-sampling-for-the-rare-and-bad.md) | Primary diagnostic | Choosing a trace sampling strategy |
| [`error-budget-is-the-decision-rule.md`](./error-budget-is-the-decision-rule.md) | Absolute rule | Deciding to ship vs. freeze for reliability |
| [`correlate-the-three-pillars.md`](./correlate-the-three-pillars.md) | Absolute rule | Instrumenting a new service |
| [`keep-on-call-humane.md`](./keep-on-call-humane.md) | Pattern | Reviewing on-call load and rotation health |
| [`control-metric-cardinality.md`](./control-metric-cardinality.md) | Absolute rule | Adding a new metric dimension |
| [`slo-review-cadence.md`](./slo-review-cadence.md) | Pattern | Running the quarterly SLO review |
| [`exemplars-link-metric-to-trace.md`](./exemplars-link-metric-to-trace.md) | Pattern | Instrumenting histograms for investigation |
| [`structured-logs-are-queryable.md`](./structured-logs-are-queryable.md) | Absolute rule | Adding logging to any service |
| [`alert-ownership-has-a-named-team.md`](./alert-ownership-has-a-named-team.md) | Absolute rule | Creating or auditing alert rules |
| [`sli-must-measure-user-pain.md`](./sli-must-measure-user-pain.md) | Absolute rule | Defining a new SLI or reviewing an existing one |
| [`sampling-strategy-before-volume-explodes.md`](./sampling-strategy-before-volume-explodes.md) | Pattern | Designing the trace pipeline for production |
| [`incident-severity-is-declared-not-debated.md`](./incident-severity-is-declared-not-debated.md) | Absolute rule | Starting or triaging an active incident |
| [`dashboards-answer-a-question.md`](./dashboards-answer-a-question.md) | Pattern | Designing or reviewing a Grafana dashboard |
| [`otel-semantic-conventions-first.md`](./otel-semantic-conventions-first.md) | Absolute rule | Adding attributes to spans, metrics, or logs |
| [`error-budget-policy-is-written-before-the-slo.md`](./error-budget-policy-is-written-before-the-slo.md) | Absolute rule | Setting a new SLO target |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
