---
name: aws-observability-and-alerting
description: "Step-by-step playbook for wiring CloudWatch metrics, alarms, dashboards, and X-Ray distributed tracing into an AWS workload — from log groups and metric filters to composite alarms and anomaly detection."
---

# AWS Observability and Alerting

## When to invoke

Use when standing up or auditing the observability layer for a new or existing AWS workload: Lambda/ECS/EKS services, RDS, and API Gateway. Pair with `aws-finops` when cost anomaly alerting is in scope.

## Step 1 — Structured logging foundation

1. Every compute resource writes **JSON-structured logs** to a CloudWatch Log Group with a **retention policy** (never `never-expire`; 30/60/90 days for app logs, 365 days for security/audit).
2. Use **Embedded Metric Format (EMF)** to emit custom metrics from logs without a separate PutMetricData call — stamp `_aws.CloudWatchMetrics` in the log event.
3. Apply a **resource tag strategy** on log groups: `Environment`, `Service`, `Team` — these become the cost/attribution axis for log insights queries.

## Step 2 — Core metric alarms (minimum set)

| Signal | Metric | Threshold trigger |
|---|---|---|
| Lambda errors | `Errors` / `Throttles` per function | p-error-rate > 1% over 5 min |
| Lambda duration | `Duration` P99 | Approaching function timeout |
| ECS/Fargate CPU | `CPUUtilization` per service | > 80% sustained 5 min |
| RDS connections | `DatabaseConnections` | > 80% of `max_connections` |
| RDS freeable memory | `FreeableMemory` | < 200 MB |
| API Gateway 5xx | `5XXError` | Any spike > 5/min |
| SQS DLQ depth | `ApproximateNumberOfMessagesVisible` on DLQ | > 0 (any message) |

Use **Composite Alarms** to reduce alarm noise: group a service's error + latency + saturation alarms under one composite that fires the SNS/PagerDuty topic.

## Step 3 — Anomaly detection on variable signals

For metrics without a hard threshold (e.g., request rate that follows day-of-week curves):

```hcl
resource "aws_cloudwatch_metric_alarm" "request_rate_anomaly" {
  alarm_name          = "${var.service}-request-rate-anomaly"
  comparison_operator = "GreaterThanUpperThreshold"
  evaluation_periods  = 3
  threshold_metric_id = "e1"

  metric_query {
    id          = "m1"
    return_data = false
    metric { ... }
  }
  metric_query {
    id          = "e1"
    expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
    return_data = true
  }
}
```

Band width `2` → ~95% confidence interval; tighten to `1.5` for latency-sensitive workloads.

## Step 4 — X-Ray distributed tracing

1. Enable **Active Tracing** on Lambda (environment variable `AWS_XRAY_SDK_ENABLED=true` or `TracingConfig: Active`).
2. For ECS: set the X-Ray daemon as a **sidecar container** with port 2000/UDP open in the task's security group.
3. Annotate segments with **service name, version, and customer/tenant id** — these become filterable in the X-Ray console and Service Map.
4. Set a **sampling rule**: 5% reservoir + 1/sec fixed rate for high-traffic paths; 100% for error paths (rule condition: `http.url` contains `/payment`).

## Step 5 — Dashboards

Build one CloudWatch Dashboard per service with:
- **Request rate + error rate + P50/P95/P99 latency** on row 1 (the RED signals).
- **Saturation signals** (CPU, memory, connections, queue depth) on row 2.
- **Downstream dependency health** (RDS, DynamoDB, external APIs via X-Ray) on row 3.
- Link the dashboard ARN in the service's runbook.

## Step 6 — Alarm routing

```
Alarm → SNS topic (per environment)
  ├── Sev-1: PagerDuty / OpsGenie (prod P99 latency, error rate, DLQ depth)
  └── Sev-2: Slack webhook (staging, cost anomalies, non-critical warnings)
```

Use **AWS Chatbot** to route CloudWatch alarms directly to Slack channels — avoids a Lambda forwarder for basic notification.

## Pitfalls

- **Setting `RetentionInDays: 0` (infinite) on log groups** — a common default that silently accumulates GBs and bill.
- **Missing DLQ depth alarms** — a silent DLQ is how async processing fails invisibly for days.
- **Composite alarms skipped** — individual alarms per metric create alert fatigue; the composite is the on-call signal, the individual alarms are the diagnostic detail.
- **X-Ray sampling at 100% in prod** — traces every request; at high throughput this adds cost and latency. Use reservoir + fixed-rate rules.
- **Dashboard with no link in the runbook** — a dashboard nobody finds during an incident has zero value.
