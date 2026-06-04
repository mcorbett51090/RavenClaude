# CDC + outbox (avoid dual-writes)

```
-- service (with backend-engineering):
BEGIN; update orders ...; insert into outbox(event,payload); COMMIT;
-- Debezium reads the DB log (outbox table) -> Kafka topic
```
- No service writes to both DB and Kafka directly.
- Events match committed DB state; order preserved per key.
