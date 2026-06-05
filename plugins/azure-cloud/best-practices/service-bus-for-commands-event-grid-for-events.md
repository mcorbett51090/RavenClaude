# Use Service Bus for commands, Event Grid for events — don't swap them

**Status:** Pattern
**Domain:** Azure integration
**Applies to:** `azure-cloud`

---

## Why this exists

Service Bus and Event Grid solve different problems, and swapping them creates either over-engineered fan-out (Service Bus for pub/sub where Event Grid fits) or under-designed reliability (Event Grid for a command that must be processed exactly once). Service Bus is a broker for **commands** — ordered, durable, exactly-once (sessions), dead-letter-able messages where a specific receiver must process each one. Event Grid is a **reactive events** backbone — a resource-state change happened, fan it out to N subscribers who may or may not care; delivery is at-least-once but not ordered, and there is no session concept.

## How to apply

**Decision shortcut:**

| Shape | Service |
|---|---|
| "Do this thing" — one processor, must not lose, may need ordering | Service Bus |
| "This thing happened" — broadcast to N subscribers, any order, idempotent consumers | Event Grid |
| High-volume streaming telemetry (millions/sec), replay, consumer groups | Event Hubs |

```bicep
// Service Bus queue for commands — FIFO + DLQ
resource sbNamespace 'Microsoft.ServiceBus/namespaces@2023-01-01-preview' = {
  name: 'sb-${appName}-${env}'
  location: location
  sku: { name: 'Standard' }
}

resource orderQueue 'Microsoft.ServiceBus/namespaces/queues@2023-01-01-preview' = {
  parent: sbNamespace
  name: 'orders'
  properties: {
    requiresDuplicateDetection: true
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount: 5
    lockDuration: 'PT1M'
  }
}

// Event Grid topic for events — fan-out to multiple subscribers
resource eventTopic 'Microsoft.EventGrid/topics@2023-12-15-preview' = {
  name: 'evgt-${appName}-${env}'
  location: location
  properties: {
    inputSchema: 'CloudEventSchemaV1_0'
  }
}
```

**Do:**
- Use `requiresDuplicateDetection: true` on Service Bus queues for idempotent command dispatch.
- Set `deadLetteringOnMessageExpiration: true` — a message that expires is a missing command.
- Use CloudEvents schema for Event Grid topics for portability and tracing.
- Route Service Bus DLQ messages to an alert so failures are noticed.

**Don't:**
- Use Event Grid for an operation where exactly-one processing matters — it is at-least-once.
- Use Service Bus for high-cardinality event fan-out (millions/hour) — it's not a streaming platform; use Event Hubs.
- Mix command and event semantics in a single topic/queue — separate them physically.
- Use Event Grid for internal high-frequency chatter — it is priced per operation.

## Edge cases / when the rule does NOT apply

- **Logic Apps / Power Automate triggers**: both support Event Grid and Service Bus triggers natively — the integration pattern remains the same, only the consumer changes.
- **Event Hubs Kafka endpoint**: use Event Hubs when you need Kafka-protocol compatibility or sub-second streaming at high volume.

## See also

- [`../agents/integration-engineer.md`](../agents/integration-engineer.md) — owns Service Bus / Event Grid / APIM selection and configuration.
- [`./ops-diagnostic-settings-to-log-analytics-from-day-one.md`](./ops-diagnostic-settings-to-log-analytics-from-day-one.md) — enable diagnostic settings on Service Bus namespaces and Event Grid topics.

## Provenance

Codifies house opinion #12 from `CLAUDE.md` §3: "Service Bus = commands, Event Grid = events, APIM = published APIs." Grounded in `knowledge/azure-integration-decision.md` and the Azure messaging services comparison documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
