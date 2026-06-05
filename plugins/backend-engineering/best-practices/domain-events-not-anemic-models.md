# Encode business intent in domain events, not anemic data objects

**Status:** Pattern
**Domain:** Domain modeling / service implementation
**Applies to:** `backend-engineering`

---

## Why this exists

An anemic domain model — plain data containers with no behavior — pushes business logic into service classes and produces code that is hard to test, easy to misuse, and impossible to reason about from the type alone. When a business action (an order placed, a subscription cancelled) is a method on a rich domain object that publishes a domain event, the intent is explicit, the invariants are enforced at the source, and downstream consumers can react without coupling to the originator's internals.

## How to apply

Model domain concepts as objects that protect their own invariants. Express transitions as named methods that return or emit domain events. The service/use-case layer orchestrates; it does not contain the business rules.

```typescript
// Anemic (bad) — logic is scattered in the service
class Order { status: string; items: Item[]; }

class OrderService {
  cancel(order: Order) {
    if (order.status !== 'placed') throw new Error('...');
    order.status = 'cancelled';
    eventBus.publish('order.cancelled', { orderId: order.id });
  }
}

// Rich domain model (good) — invariants + events live in the aggregate
class Order {
  private status: OrderStatus;

  cancel(): DomainEvent[] {
    if (this.status !== OrderStatus.Placed) {
      throw new InvalidOperationError('Only placed orders can be cancelled');
    }
    this.status = OrderStatus.Cancelled;
    return [new OrderCancelledEvent(this.id, new Date())];
  }
}
```

**Do:**
- Name events in the past tense: `OrderCancelled`, `PaymentFailed`, `InventoryReserved`.
- Keep domain events serializable and immutable — they are facts, not commands.
- Route domain events through the outbox pattern before publishing externally.
- Let each aggregate enforce its own invariants; service methods orchestrate aggregates, not field-sets.

**Don't:**
- Put `if/else` business logic in service classes that directly mutate plain data fields.
- Use `Updated` or `Changed` as event names — these describe the what, not the why.
- Publish domain events directly to the broker inside a transaction; use the outbox to avoid dual-write loss.

## Edge cases / when the rule does NOT apply

CRUD-only microservices (a settings store, a config service) with no domain invariants and no downstream consumers benefit little from domain events; a simple repository pattern is correct there. Also, within a query/read side there are no domain events — these are a write-side construct.

## See also

- [`../agents/service-implementation-engineer.md`](../agents/service-implementation-engineer.md) — owns business-logic layering.
- [`./use-the-outbox-for-write-then-publish.md`](./use-the-outbox-for-write-then-publish.md) — the safe path to externalize domain events without dual-write loss.

## Provenance

Codifies Domain-Driven Design (Eric Evans, Vaughn Vernon) applied to `service-implementation-engineer`'s responsibility for clean domain modeling. Complements the outbox and idempotency rules in this plugin.

---

_Last reviewed: 2026-06-05 by `claude`_
