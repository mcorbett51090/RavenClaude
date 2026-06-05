# Use the outbox pattern to guarantee payment event delivery

**Status:** Pattern
**Domain:** Money operations / reliability
**Applies to:** `fintech-payments-engineering`

---

## Why this exists

A payment service that updates the database and then publishes an event to a
queue or webhook destination in two separate operations has a reliability gap:
the database write can succeed while the event publish fails (network error,
queue unavailability, process crash after commit). The ledger is updated but
downstream systems (billing, revenue recognition, email) never receive the
event. This is the "dual-write problem." In payment systems where downstream
consumers (revenue recognition, order fulfillment) depend on the event, a
missed event is a lost revenue record or an unfulfilled order.

## How to apply

Write the outgoing event to an `outbox` table in the **same database
transaction** as the money operation. A separate relay process polls the outbox
and delivers events, marking them delivered on success.

```sql
-- In the same transaction as the ledger write:
BEGIN;

INSERT INTO ledger_entries (id, account, amount_cents, currency, type, created_at)
VALUES ($1, $2, $3, $4, 'charge', NOW());

INSERT INTO outbox (id, event_type, payload, created_at, delivered)
VALUES (gen_random_uuid(), 'payment.succeeded',
        '{"charge_id":"ch_xxx","amount_cents":4999,"currency":"USD"}',
        NOW(), FALSE);

COMMIT;
```

```python
# Outbox relay (runs independently — poll + deliver + mark)
def relay_outbox():
    events = db.query("SELECT * FROM outbox WHERE delivered = FALSE ORDER BY created_at LIMIT 100")
    for event in events:
        try:
            publish(event)  # idempotent consumer required
            db.execute("UPDATE outbox SET delivered = TRUE WHERE id = %s", event.id)
        except Exception:
            log_failure(event)  # retry next poll
```

Consumers must be idempotent (deduplicate by event id) because the relay may
deliver the same event more than once on retry.

**Do:**
- Write the outbox entry in the same database transaction as the money operation.
- Use an idempotency key (the outbox row id) so the relay can safely retry.
- Monitor outbox queue depth as an SLI: growing depth signals relay failure.

**Don't:**
- Publish directly to a queue after a database commit — the dual-write race is
  real.
- Deliver events without idempotency on the consumer side.
- Let the outbox table grow unbounded — archive delivered rows on a schedule.

## Edge cases / when the rule does NOT apply

- Services using an event-sourced architecture (the event log IS the state):
  the outbox is the event log and the delivery is built into the event-sourcing
  infrastructure.

## See also

- [`../agents/payments-architect.md`](../agents/payments-architect.md) — owns payment system architecture
- [`./every-money-operation-is-idempotent.md`](./every-money-operation-is-idempotent.md) — outbox consumers must be idempotent
- [`./double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) — the ledger write and the outbox write are atomic

## Provenance

Standard transactional outbox pattern from microservices architecture literature
(Chris Richardson, "Microservices Patterns"). Applied specifically to payment
event delivery where missed events create revenue-record inconsistencies. The
dual-write problem is a well-documented distributed systems failure mode.

---

_Last reviewed: 2026-06-05 by `claude`_
