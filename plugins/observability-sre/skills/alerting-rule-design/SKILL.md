---
name: alerting-rule-design
description: "Playbook for writing alerts that page on user-visible symptoms using multi-window multi-burn-rate rules — covering threshold selection, alert fatigue reduction, and runbook requirements."
---

# Alerting Rule Design

## When to Use This Skill

When a team needs to write or audit alert rules — choosing between symptom-based vs cause-based alerting, setting burn-rate thresholds, and eliminating noise alerts that erode on-call trust.

## Core Principle: Alert on Symptoms, Not Causes

| Wrong (cause) | Right (symptom) |
|---|---|
| CPU > 80% for 5 min | Error rate > SLO threshold |
| Memory pressure | Latency p99 > budget |
| Pod OOMKilled | Availability SLO burning |
| Disk I/O wait > threshold | Request success rate < target |

A cause alert may fire harmlessly; a symptom alert always means users are experiencing pain.

## Multi-Window Multi-Burn-Rate Template

For an SLO with a 30-day error budget, use four alert rules:

| Severity | Burn rate | Short window | Long window | Action |
|---|---|---|---|---|
| P1 (page now) | 14x | 1 h | 5 min | Wake on-call immediately |
| P2 (page) | 6x | 6 h | 30 min | Page during business hours |
| P3 (ticket) | 3x | 1 d | 2 h | Create ticket, no page |
| P4 (info) | 1x | 3 d | 6 h | Dashboard annotation only |

**Burn rate formula:** `burn_rate = error_rate / (1 - SLO_target)`

A 14x burn rate on a 99.9% SLO means 1.4% errors — budget exhausted in ~2 days.

**Prometheus rule example (P1):**

```yaml
- alert: HighErrorBudgetBurnRate
  expr: |
    (
      job:request_errors:rate1h{job="api"} / job:request_count:rate1h{job="api"}
      > 14 * (1 - 0.999)
    )
    and
    (
      job:request_errors:rate5m{job="api"} / job:request_count:rate5m{job="api"}
      > 14 * (1 - 0.999)
    )
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Error budget burning at 14x rate"
    runbook_url: "https://runbooks.internal/api-error-budget"
```

## Alert Quality Checklist

Every alert rule must answer yes to all five:

- [ ] **Actionable:** Does the on-call engineer know what to do within 5 minutes of receiving this?
- [ ] **Urgent:** Is this worth waking someone at 3 AM? If not, it should not page.
- [ ] **Symptom-based:** Does it measure user-visible impact, not internal cause?
- [ ] **Has a runbook:** The `runbook_url` annotation links to a document with diagnosis steps and escalation path.
- [ ] **Has been tested:** A test against the alert expression confirmed it fires on a known-bad signal.

## Runbook Minimum Requirements

Every pageable alert must have a runbook that includes:

1. **What it means** — plain-language description of the user impact
2. **Diagnosis steps** — ordered list of what to check, with links to dashboards
3. **Mitigation options** — what can be done to stop the bleeding (feature flag, rollback, scaling)
4. **Escalation path** — who to call if you can't resolve in 30 minutes

## Alert Fatigue Audit

Run this audit quarterly on the alerting ruleset:

1. Pull the last 30 days of alert firings.
2. For each alert: count pages, count actionable pages (where on-call took an action), compute the signal ratio.
3. Any alert with signal ratio < 50% is a noise alert — silence, fix the root cause, or delete.
4. Any alert that fired > 20 times without escalating to an incident is likely a false positive.

## Pitfalls

- Setting `for: 0m` on a high-severity alert — spike noise pages. Use at least 2–5 minutes for P1; 15–30 for P2.
- Writing a single alert at a fixed threshold without a short + long window — misses slow burns and misfires on spikes.
- Alerts without `runbook_url` — on-call stares at a metric with no guidance.
- Alerting on individual pod/instance metrics instead of service-level aggregates — triggers at the wrong scale.

## See also

- [../../agents/sre-reliability-engineer.md](../../agents/sre-reliability-engineer.md) — SLO/error-budget design and burn-rate alerting
- [../../agents/observability-engineer.md](../../agents/observability-engineer.md) — metrics pipeline and recording rules
- [../../CLAUDE.md](../../CLAUDE.md) — house opinions on symptom-based alerting
