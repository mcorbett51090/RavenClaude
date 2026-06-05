# Avoid distributed transactions — design for eventual consistency instead

**Status:** Absolute rule
**Domain:** Service architecture / data consistency
**Applies to:** `backend-engineering`

---

## Why this exists

A distributed transaction (2PC, saga with rollback-coordination, or a synchronous write spanning two services) creates a consistency coupling between services that undermines the availability and fault-isolation benefits of splitting them. When one participant is unavailable, the entire transaction hangs or rolls back — you've built a system that is only as available as its least-available component. The outbox pattern, idempotent consumers, and sagas with compensation are the tools that achieve safe eventual consistency without the coupling of 2PC.

## How to apply

Write to your local database and publish an event via the outbox in a single local transaction. Let downstream services react asynchronously.

```
# What to avoid:
BEGIN distributed transaction across Service A + Service B;
  INSERT into A.orders;
  RPC to B: reserve inventory;  # if B is down — A is blocked too
COMMIT both;

# What to do instead:
# Service A:
BEGIN local transaction;
  INSERT into orders (status = 'pending');
  INSERT into outbox (event = 'OrderPlaced', payload = ...);
COMMIT;
# Outbox relay publishes OrderPlaced to the broker.

# Service B (async consumer, idempotent):
ON OrderPlaced:
  reserve inventory;
  publish InventoryReserved (or InventoryUnavailable);
```

Use a saga with compensation (publish a `CancelOrder` event) if downstream steps fail after the initial write.

**Do:**
- Accept that a cross-service write produces intermediate states (order placed but inventory not yet reserved).
- Design UX around eventual consistency — show a "processing" state, not a hard success/fail at the first write.
- Make every downstream consumer idempotent so redelivery is safe.
- Use outbox → relay → broker to guarantee at-least-once delivery without dual-write loss.

**Don't:**
- Use 2PC between microservices — it creates tighter availability coupling than a monolith.
- Chain synchronous RPC calls for a multi-step write as a substitute for a distributed transaction.
- Leave partial saga state without a defined compensation path.

## Edge cases / when the rule does NOT apply

Within a single service's own database, local transactions are correct and encouraged. A saga is unnecessary if the entire operation can be expressed in one ACID local transaction.

## See also

- [`../agents/backend-architect.md`](../agents/backend-architect.md) — service boundary and consistency design.
- [`./use-the-outbox-for-write-then-publish.md`](./use-the-outbox-for-write-then-publish.md) — the implementation pattern that makes eventual consistency safe.

## Provenance

CAP theorem and distributed systems design fundamentals (Martin Kleppmann's _Designing Data-Intensive Applications_). Codifies the `backend-architect` and `backend-data-access-engineer` position that distributed transactions are an availability hazard, not a correctness tool.

---

_Last reviewed: 2026-06-05 by `claude`_
