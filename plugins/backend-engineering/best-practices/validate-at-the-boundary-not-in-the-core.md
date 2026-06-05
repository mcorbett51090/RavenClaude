# Validate at the Boundary, Not in the Core

**Status:** Absolute rule
**Domain:** service implementation
**Applies to:** `backend-engineering`

---

## Why this exists

Input validation that lives deep in a service or domain object is called too late: the invalid data has already crossed the system boundary, possibly been logged, and may have partially mutated state. Validation at the inbound boundary (controller/handler layer, queue consumer, event subscriber) rejects bad input before it reaches the core, giving the caller a clear, actionable error rather than a mid-operation exception.

## How to apply

Validate the full shape and constraints of inbound data at the first point of entry — the HTTP handler, the queue consumer, or the event subscriber — before passing anything into the service layer. Use a schema/validation library rather than hand-written if-chains; it is declarative, composable, and testable independently.

```python
# FastAPI / Pydantic example — validation at the handler boundary
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class PlaceOrderRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0, le=Decimal("100000"))
    idempotency_key: str = Field(..., min_length=8, max_length=128)

    @validator("amount")
    def two_decimal_places(cls, v):
        if v.as_tuple().exponent < -2:
            raise ValueError("amount must have at most 2 decimal places")
        return v

# Controller — validation happens here, domain receives clean data
@router.post("/orders", status_code=201)
def place_order(body: PlaceOrderRequest):
    order = order_service.place_order(
        user_id=body.user_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
    )
    return serialize(order)
```

**Do:**
- Define validation schemas per operation/command, not one mega-schema reused everywhere.
- Return all validation errors in one response pass (not stop-on-first) so the caller can fix everything at once.
- Validate queue messages at the consumer boundary before processing — a malformed message should DLQ, not error mid-processing.

**Don't:**
- Re-validate the same input again inside the service or domain — trust the boundary contract.
- Use generic `400 Bad Request` without a field-level error detail; tell the caller which field failed and why.
- Let the service layer raise `ValueError` that the controller catches and guesses about — those are domain exceptions, not validation errors.

## Edge cases / when the rule does NOT apply

Domain invariants (e.g., "a user cannot have more than 10 open orders") are business rules, not input validation — they belong in the service layer and produce domain exceptions, not boundary validation errors. The distinction: boundary validation checks shape, type, and range; domain validation checks business state.

## See also

- [`../agents/service-implementation-engineer.md`](../agents/service-implementation-engineer.md) — owns the layering that makes boundary validation the single gate.
- [`./model-errors-explicitly.md`](./model-errors-explicitly.md) — validation errors need a consistent error model to return to callers.

## Provenance

Codifies the `service-implementation-engineer` concern in CLAUDE.md §2: "validation" as an explicit responsibility. Standard layered architecture practice; aligns with the Ports and Adapters principle that adapters own input transformation and validation before the core sees the data.

---

_Last reviewed: 2026-06-05 by `claude`_
