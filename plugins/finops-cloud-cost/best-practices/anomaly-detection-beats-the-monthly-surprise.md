# Anomaly detection beats the monthly surprise

**Status:** Pattern
**Domain:** Cloud cost monitoring and alerting
**Applies to:** `finops-cloud-cost`

---

## Why this exists

A monthly cloud bill review is a lagging indicator. By the time the bill arrives, the incident that
caused a cost spike is 2–6 weeks old. The misconfigured NAT gateway that cost $40,000 in a week,
the runaway batch job, the viral AI feature that exhausted the monthly inference budget in 5 days —
all of these are discoverable within hours if anomaly detection is in place. Without it, they become
a post-mortem conversation at month end.

Cost spikes also compound: a misconfiguration left running for 3 weeks generates 3× the cost of
one discovered in the first day. Early detection is not just better; it is materially cheaper.

The monthly review still has value — for trend analysis, commitment reviews, and strategic
optimization. But it is not a substitute for real-time or daily anomaly alerting.

## How to apply

- Define a baseline: a rolling 7–14 day average of daily cloud spend (or spend per service/team).
- Set a threshold: z-score > 2 (two standard deviations above the rolling mean) or a simpler
  percentage threshold (>150% of the rolling 7-day average). Use `scripts/finops_calc.py
  anomaly_z_score()` for the z-score calculation.
- Set the alert cadence: check daily (not hourly for most workloads; hourly for AI inference or
  event-driven architectures). Native cloud tools (AWS Cost Anomaly Detection, Azure Cost alerts)
  operate with a lag of 24–48 hours [verify-at-use]; supplement with CloudWatch/Monitor metrics
  on key cost drivers for sub-hour detection.
- Route the alert: the on-call engineer AND the FinOps team, with a brief runbook: (a) identify
  the service and resource via the cost anomaly report, (b) check for a known event (deployment,
  traffic spike), (c) escalate to the resource owner if unknown.
- Set AI-specific thresholds separately: AI inference cost can spike 10–100× more sharply than
  compute. A separate alert on daily inference spend, with a tighter threshold, is warranted.

**Do:**

- Wire anomaly alerting to the on-call rotation — cost anomalies are operational incidents.
- Use the native cloud anomaly detection tools as the first layer; they require zero instrumentation.
  [verify-at-use: capability and latency differ by provider]
- Establish a "cost incident" response runbook alongside your SRE runbooks.
- Review and tune thresholds quarterly — a growing workload will have a higher baseline and the
  same threshold may generate false positives.

**Don't:**

- Rely on a monthly bill review as the primary anomaly discovery mechanism.
- Set anomaly thresholds so high (e.g., >500% of baseline) that they only fire on catastrophic
  incidents while missing expensive but gradual cost drift.
- Route cost anomaly alerts only to Finance — engineers who can take action must be in the loop.
- Treat a triggered anomaly alert as an inconvenience — investigate every alert with the same
  discipline as an SLO breach.

## Edge cases / when the rule does NOT apply

For small, stable workloads with very low cloud spend (e.g., a startup with $2,000/month total
cloud cost), a weekly manual review is a reasonable substitute for automated anomaly detection.
Set a manual threshold: "if this week's cost is >30% higher than last week's, investigate."
The automation investment becomes worthwhile at approximately $10,000/month in cloud spend where
the cost of a missed anomaly exceeds the cost of tooling. [verify-at-use: this threshold is
illustrative; calibrate to the organization's risk tolerance]

## See also

- [`./ai-token-cost-is-a-first-class-budget-line.md`](./ai-token-cost-is-a-first-class-budget-line.md)
- [`../scripts/finops_calc.py`](../scripts/finops_calc.py) — `anomaly_z_score()` function
- [`../knowledge/finops-cloud-cost-decision-trees.md`](../knowledge/finops-cloud-cost-decision-trees.md) — 2026 capability map (anomaly detection tools)

## Provenance

Reflects FinOps Foundation operate-phase monitoring guidance and the observed industry pattern
of cost anomalies discovered weeks late when relying on monthly billing cycles. The z-score
threshold recommendation is a practical starting point from statistical process control applied
to cost time-series data.

---

_Last reviewed: 2026-06-08 by `claude`._
