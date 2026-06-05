# Dead-Letter Queues Are Mandatory

**Status:** Absolute rule
**Domain:** background jobs and messaging
**Applies to:** `backend-engineering`

---

## Why this exists

A message queue without a dead-letter queue (DLQ) silently discards or infinitely retries poison messages. Both outcomes are worse than the failure itself: silent discard means unprocessed work vanishes without an alert; infinite retry holds worker capacity and masks the root cause. A DLQ is the observable, recoverable failure mode for async work.

## How to apply

Every consumer queue gets a paired DLQ at provisioning time. Configure a max-delivery-count (typically 3–5); after that many failures the broker routes the message to the DLQ. Alert on DLQ depth greater than zero so on-call knows immediately. Keep the original message headers and a failure reason alongside the dead-lettered message so replay is possible without guesswork.

```yaml
# AWS SQS example (CloudFormation/SAM)
OrderQueue:
  Type: AWS::SQS::Queue
  Properties:
    VisibilityTimeout: 30
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt OrderDLQ.Arn
      maxReceiveCount: 3   # 3 delivery attempts before DLQ

OrderDLQ:
  Type: AWS::SQS::Queue
  Properties:
    MessageRetentionPeriod: 1209600   # 14 days — time to investigate + replay

# CloudWatch alarm on DLQ depth
DLQAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    MetricName: ApproximateNumberOfMessagesVisible
    Namespace: AWS/SQS
    Dimensions:
      - Name: QueueName
        Value: !GetAtt OrderDLQ.QueueName
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```

**Do:**
- Alert (PagerDuty / SNS) when DLQ depth crosses 1 — any dead-lettered message is a signal.
- Retain DLQ messages long enough to investigate and replay (14 days is a common floor).
- Build a replay mechanism before you need it; a DLQ with no replay is just a slower discard.
- Include the original message payload, timestamp, and exception in the DLQ record.

**Don't:**
- Provision a queue without a DLQ "just to keep it simple."
- Set `maxReceiveCount` to 1 — transient failures (network blip, cold start) will incorrectly DLQ good messages.
- Let consumer code catch-all exceptions and ack the message; re-raise so the broker routes to DLQ.

## Edge cases / when the rule does NOT apply

Fire-and-forget metrics/telemetry queues where message loss is acceptable by design may skip the DLQ — but document the intent explicitly so the next engineer doesn't wonder. Pure in-process job queues (no broker) use DLQ-equivalent error tables or retry logs instead.

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns background-job/worker design including DLQ provisioning.
- [`./queues-need-backpressure-and-a-dlq.md`](./queues-need-backpressure-and-a-dlq.md) — companion rule on queue backpressure alongside DLQ.

## Provenance

Codifies the `backend-reliability-engineer` section on background-job/worker design in CLAUDE.md §2 rule 4 and the `queues-need-backpressure-and-a-dlq` existing rule. Standard broker pattern (AWS SQS, Azure Service Bus, RabbitMQ all implement DLQ natively).

---

_Last reviewed: 2026-06-05 by `claude`_
