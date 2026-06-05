# Set CloudWatch alarms, not just dashboards

**Status:** Absolute rule
**Domain:** AWS observability / ops
**Applies to:** `aws-cloud`

---

## Why this exists

Dashboards require a human to look at them; alarms act without one. The most common observability gap on AWS is a beautifully instrumented CloudWatch console that nobody checks until an incident is already in progress. Without alarms, high-latency spikes, error-rate surges, and cost overruns are discovered in retrospect. A metric that is not wired to an alarm is decoration, not observability.

## How to apply

For every workload in production, set alarms on at minimum:

1. **Error rate** — e.g., Lambda error %, ALB 5xx rate, SQS `NumberOfMessagesFailed`
2. **Latency P99** — ALB/API Gateway `P99Latency`, Lambda `P99Duration`
3. **Queue depth** — SQS `ApproximateNumberOfMessagesVisible` above a safe threshold
4. **CPU/memory** — EC2/ECS/EKS nodes at ≥ 80% sustained for 5+ minutes
5. **DLQ depth** — any DLQ receiving messages is a signal, not a queue to drain silently

```yaml
# CloudFormation snippet — ALB 5xx alarm
HighErrorRateAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub "${AWS::StackName}-high-5xx"
    MetricName: HTTPCode_Target_5XX_Count
    Namespace: AWS/ApplicationELB
    Dimensions:
      - Name: LoadBalancer
        Value: !GetAtt ALB.LoadBalancerFullName
    Statistic: Sum
    Period: 60
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref OpsAlertTopic
    TreatMissingData: notBreaching
```

**Do:**
- Wire alarms to an SNS topic that feeds on-call (PagerDuty/OpsGenie/email).
- Use `TreatMissingData: notBreaching` for expected zero-traffic periods; `breaching` when absence of data is itself the incident.
- Set alarms in IaC alongside the resource they cover, not as a separate ops step.
- Use Composite Alarms to reduce alert noise (child alarms AND'd together).

**Don't:**
- Create alarms that only fire into an SNS topic no one subscribes to.
- Use only the default CloudWatch console — alarms do not exist there by default.
- Set alarms only at the account level and ignore per-service signal.
- Treat a dashboard as an acceptable substitute for an alarm.

## Edge cases / when the rule does NOT apply

- **Ephemeral/one-off batch jobs** with a defined runtime: a completion-check via EventBridge rule + Step Functions catch may be more useful than an ongoing CloudWatch alarm.
- **Pure dev environments** with no SLA: monitoring overhead may outweigh the benefit, but the alarm definition should still exist in IaC, scoped off by a feature flag or environment parameter.

## See also

- [`../agents/aws-ops-finops-engineer.md`](../agents/aws-ops-finops-engineer.md) — owns CloudWatch/X-Ray observability and alerting design.
- [`./budget-alarms-before-the-bill.md`](./budget-alarms-before-the-bill.md) — the complementary cost alarm rule.

## Provenance

Codifies the observability leg of `aws-ops-finops-engineer`'s remit in `CLAUDE.md` §1: "CloudWatch/X-Ray observability hooks" as a first-class output. Standard AWS Well-Architected Operational Excellence practice: instrument, alarm, respond.

---

_Last reviewed: 2026-06-05 by `claude`_
