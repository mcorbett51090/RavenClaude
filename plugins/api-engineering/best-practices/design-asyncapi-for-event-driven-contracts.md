# Use AsyncAPI 3.0 to define event-driven and webhook contracts

**Status:** Absolute rule
**Domain:** API design / event-driven
**Applies to:** `api-engineering`

---

## Why this exists

Event-driven APIs — webhooks, Kafka topics, AMQP queues, WebSocket channels — are APIs. They have a contract: a channel name, a message schema, a delivery guarantee, and an ordering model. Without a machine-readable contract (AsyncAPI), consumers must read prose documentation and guess at field names, enumerate over test traffic, and detect breaking changes by accident. An AsyncAPI 3.0 document is to event-driven APIs what OpenAPI is to REST: the source of truth for mock generation, contract testing, SDK generation, and documentation. `[verify-at-build]` — AsyncAPI 3.0 was released 2023-11; tooling is maturing.

## How to apply

```yaml
# asyncapi: '3.0.0' [verify-at-build]
asyncapi: '3.0.0'
info:
  title: Order Events API
  version: '1.0.0'

channels:
  order-placed:
    address: orders.placed
    messages:
      OrderPlaced:
        $ref: '#/components/messages/OrderPlaced'

operations:
  publishOrderPlaced:
    action: send
    channel:
      $ref: '#/channels/order-placed'

components:
  messages:
    OrderPlaced:
      payload:
        type: object
        required: [orderId, customerId, placedAt]
        properties:
          orderId: { type: string, format: uuid }
          customerId: { type: string, format: uuid }
          placedAt: { type: string, format: date-time }
          totalAmount: { type: number }
```

**Do:**
- Write the AsyncAPI document before wiring the broker topic.
- Include the message schema, channel address, bindings (Kafka partition key, AMQP exchange), and delivery semantics.
- Generate mock consumers from the spec (AsyncAPI Generator, Microcks) for contract testing.
- Version event schemas using a separate `version` field inside the message payload — channel names are stable.

**Don't:**
- Describe event-driven APIs only in prose documentation — prose cannot drive mock generation or linting.
- Skip the `operations` section: AsyncAPI 3.0 separates operations from channels to clarify send vs receive.
- Use AsyncAPI 2.x for new contracts — 3.0 is the current major.

## Edge cases / when the rule does NOT apply

Simple internal pub/sub with a single producer and consumer where the teams are co-located may use a shared type package instead of a formal AsyncAPI doc — but as soon as a second consumer appears, the contract should be formalized.

## See also

- [`../agents/api-design-architect.md`](../agents/api-design-architect.md) — owns event-driven contract design.
- [`./design-contract-first-not-code-first.md`](./design-contract-first-not-code-first.md) — contract-first applies to event APIs just as to REST.

## Provenance

AsyncAPI 3.0.0 specification (asyncapi.com). Codifies CLAUDE.md §3 paradigm-selection rule for event-driven APIs and `api-design-architect`'s contract-first posture.

---

_Last reviewed: 2026-06-05 by `claude`_
