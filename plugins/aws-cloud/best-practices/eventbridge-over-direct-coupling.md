# Route async events through EventBridge, not direct service-to-service calls

**Status:** Pattern
**Domain:** AWS event-driven integration
**Applies to:** `aws-cloud`

---

## Why this exists

Direct Lambda→Lambda invocations, SDK calls from one service to another, and SNS fan-out with no schema registry create tight coupling that is fragile when producers change. Amazon EventBridge is the AWS-native event bus: producers publish events by type, consumers subscribe by rule — neither knows about the other. This decoupling lets producers and consumers evolve independently, enables multiple consumers to react to the same event without the producer managing a fan-out list, and provides a built-in schema registry, replay, and dead-letter path. Skipping EventBridge in favor of direct invocation is an architectural debt that compounds as the number of integrations grows.

## How to apply

1. Define a schema for your event in the Schema Registry (JSON Schema or OpenAPI). Version it.
2. Producer publishes to a custom event bus with a `detail-type` and `source` that identifies the domain and event type.
3. Consumer declares an EventBridge rule matching on `detail-type` and/or `source`; the rule targets the consumer (Lambda, SQS queue, Step Functions, etc.).

```json
{
  "source": ["com.acme.orders"],
  "detail-type": ["OrderPlaced"],
  "detail": {
    "currency": ["USD"]
  }
}
```

Add a DLQ on every rule target so unprocessed events don't vanish.

**Do:**
- Use a **custom event bus** per domain (not the default bus, which mingles AWS service events with your own).
- Register the event schema in EventBridge Schema Registry before the first producer ships.
- Set a DLQ (SQS queue) on every rule target.
- Use EventBridge Pipes for point-to-point with filtering/enrichment before the target.
- For **commands** (one producer → one consumer, must be processed) prefer SQS; EventBridge is for events (facts that happened, 0-N consumers).

**Don't:**
- Invoke Lambda directly from Lambda for async cross-domain calls — it hides failures.
- Fan-out by having the producer explicitly call each consumer.
- Put secrets or large payloads (>256 KB) in the event body — reference an S3 object or a DynamoDB item instead.
- Use the default event bus for your application events (AWS service events will pollute the bus).

## Edge cases / when the rule does NOT apply

Synchronous request/response (e.g., an API call that must return a result to the caller) is not an event; use API Gateway → Lambda or a synchronous SDK call. Very high-throughput streaming (millions of events/sec) is better served by Kinesis Data Streams, not EventBridge.

## See also

- [`../agents/aws-compute-platform-engineer.md`](../agents/aws-compute-platform-engineer.md) — owns the compute (Lambda/ECS/Step Functions) that consumes the events
- [`./idempotency-and-dlqs-for-async.md`](./idempotency-and-dlqs-for-async.md) — every EventBridge consumer must be idempotent and every target must have a DLQ

## Provenance

Codifies AWS Well-Architected Reliability Pillar (loose coupling) and the house opinion "Event/spiky → Lambda; decouple with EventBridge/SQS/SNS" from `aws-cloud/CLAUDE.md` §2. Schema Registry and custom bus are standard AWS landing-zone integration patterns.

---

_Last reviewed: 2026-06-05 by `claude`_
