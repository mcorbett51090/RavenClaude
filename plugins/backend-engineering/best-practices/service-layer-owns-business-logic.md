# Service Layer Owns Business Logic

**Status:** Absolute rule
**Domain:** service implementation
**Applies to:** `backend-engineering`

---

## Why this exists

Business logic scattered across controllers, models, and query callbacks becomes untestable, non-reusable, and impossible to reason about as the system grows. When a controller action or an ORM callback owns a business rule, that rule cannot be tested without an HTTP request or a database round-trip. The service/use-case layer is the seam where logic lives independently of the framework.

## How to apply

Place every meaningful business operation in an explicit service class or use-case function. The controller (or handler) translates the HTTP request into a plain domain object, calls the service, and translates the result back into a response. The service knows nothing about HTTP, nothing about the ORM mapping layer, and nothing about the presentation format.

```python
# BAD: business logic in a controller
class OrderController:
    def create(self, request):
        if request.user.credit_limit < request.json["amount"]:
            return 400, {"error": "over limit"}
        order = Order(user=request.user, amount=request.json["amount"])
        order.save()
        notify_warehouse(order)
        return 201, order.to_dict()

# GOOD: thin controller, logic in a service
class OrderService:
    def place_order(self, user: User, amount: Decimal) -> Order:
        if user.credit_limit < amount:
            raise CreditLimitExceeded(user_id=user.id, amount=amount)
        order = self.order_repo.create(user_id=user.id, amount=amount)
        self.event_bus.publish(OrderPlaced(order_id=order.id))
        return order

class OrderController:
    def create(self, request):
        order = self.order_service.place_order(
            user=request.user,
            amount=Decimal(request.json["amount"]),
        )
        return 201, serialize(order)
```

**Do:**
- Name services after the business capability they represent (`OrderService`, `PaymentProcessor`) not the framework concern (`OrderController`, `OrderModel`).
- Keep service methods returning domain objects or raising domain exceptions — not HTTP responses or ORM instances.
- Write unit tests for the service in isolation; mock the repo and event bus.

**Don't:**
- Import framework types (request, response, session) into the service layer.
- Let ORM model methods grow business rules — `user.can_place_order()` is a service concern.
- Call one service from another when shared logic exists; extract a third service or a domain function.

## Edge cases / when the rule does NOT apply

Pure CRUD endpoints with no business rules (e.g., admin list/get) may be thin enough that a dedicated service adds ceremony without value. Apply judgement — the rule is violated when the logic is meaningful enough to test independently.

## See also

- [`../agents/service-implementation-engineer.md`](../agents/service-implementation-engineer.md) — owns this layering pattern end-to-end.
- [`./model-errors-explicitly.md`](./model-errors-explicitly.md) — domain exceptions raised by the service layer need an explicit error model.

## Provenance

Codifies the `service-implementation-engineer` and `backend-architect` house opinions from CLAUDE.md §2 rule 2: "Model the domain, then the code" and §2 generally. Standard Clean Architecture / hexagonal architecture principle.

---

_Last reviewed: 2026-06-05 by `claude`_
