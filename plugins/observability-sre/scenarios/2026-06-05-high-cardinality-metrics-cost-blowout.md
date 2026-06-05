---
scenario_id: 2026-06-05-high-cardinality-metrics-cost-blowout
contributed_at: 2026-06-05
plugin: observability-sre
product: prometheus
product_version: "unknown"
scope: likely-general
tags: [cardinality, metrics-cost, tsdb, label, time-series, prometheus]
confidence: high
reviewed: false
---

## Problem

A team's managed-metrics bill roughly tripled over one quarter and the Prometheus instances started OOM-killing during compaction. The active series count had grown from ~2M to ~28M with no corresponding growth in services or traffic. The on-call's first instinct was "we need bigger Prometheus boxes / a higher metrics-vendor tier" — i.e. pay for the explosion rather than find it.

## Constraints context

- Self-hosted Prometheus + remote-write to a managed, per-active-series-billed backend.
- A recent release had added a `user_id` label and a `request_path` label to the HTTP request-duration histogram "to make dashboards more granular."
- `request_path` carried the raw path including IDs (`/orders/8a3f.../items`), so it was effectively unbounded; `user_id` was unbounded by definition.
- A histogram with 12 buckets × the new label cross-product meant each unbounded label multiplied the series count by its distinct-value count, then again per bucket.

## Attempts

- Tried: vertically scaling Prometheus (more RAM) and bumping the vendor tier. Bought ~3 weeks before the next OOM and a bigger bill — treating the symptom (series volume) instead of the cause (an unbounded label). Series count is a *product*, so scaling can't outrun it.
- Tried: dropping the retention window from 15d to 5d. Reduced storage but not the active-series count (the billing driver) or the compaction OOM, which is driven by *active* series, not retention depth. Wrong lever.
- Tried (the move that worked): ran a cardinality audit (`topk` on `count by (__name__)` and per-label `count(count by (label)(metric))`) to find the offenders, confirmed `request_path` and `user_id` on the request histogram were ~95% of the new series, then (a) dropped both labels from the *metric*, (b) moved that high-cardinality detail to **traces and exemplars** (where per-request `user_id` and the real path belong), and (c) added a templated, bounded `route` label (`/orders/{id}/items`) for the dashboard granularity the team actually wanted. Added a relabel/drop rule at the scrape/remote-write boundary as a backstop and set an explicit cardinality budget with an alert on series growth.

## Resolution

**Cardinality is a multiplication, so the fix is finding the unbounded label, not buying more capacity.** The per-request detail the team wanted (which user, which exact path) is real and worth keeping — it just belongs on **traces/logs**, not as a **metric label**. The recipe:

1. **Audit, don't scale.** Find the top series-count contributors and the per-label distinct-value counts. The blowout is almost always one or two unbounded labels (user/request/session id, raw path, full URL, error message as a label).
2. **Move high-cardinality detail to the right pillar.** A per-request id or raw path on a *metric* is the canonical foot-gun — that data wanted to be a **trace attribute / log field** all along, with an **exemplar** linking the metric spike to an example trace. Metrics are for bounded, aggregatable dimensions.
3. **Template or bucket what must stay a label.** `/orders/{id}/items` (templated route) and status-class (`2xx`/`5xx`) are bounded; the raw path and raw status code are not.
4. **Backstop at the boundary + set a budget.** A relabel/drop rule at scrape or remote-write stops a regression from reaching the billed backend, and an explicit cardinality budget + a series-growth alert turn the next blowout into a page before it's a bill.

Active series dropped from ~28M back to ~3M, the OOMs stopped, the bill returned near baseline, and the team kept the dashboard granularity they actually needed via the templated `route` label + traces for the per-user drill-down.

**Action for the next engineer:** when a metrics bill or a TSDB falls over, **count series before you scale anything.** The cause is nearly always an unbounded label that wanted to be a trace attribute. Scaling pays for the bug; the audit fixes it.

Cross-reference: [`../knowledge/observability-sre-decision-trees.md`](../knowledge/observability-sre-decision-trees.md) `## Decision Tree: Cardinality — label or attribute?` and `## Decision Tree: Logs, metrics, or traces — which pillar for this question?`. This is the field-note complement to the best-practices `control-metric-cardinality.md` and `set-an-explicit-cardinality-budget.md`. The instrumentation lane is `observability-engineer`'s; the in-cluster metrics pipeline belongs to `cloud-native-kubernetes`.

**Sources for the cited pattern:** Prometheus docs, "Instrumentation — use labels" / cardinality guidance — https://prometheus.io/docs/practices/instrumentation/#use-labels and naming/cardinality at https://prometheus.io/docs/practices/naming/ (retrieved 2026-06-05). Series counts and bill figures are illustrative for this engagement; validate against the team's own TSDB stats before a deliverable.
