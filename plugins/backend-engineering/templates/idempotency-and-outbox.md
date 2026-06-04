# Idempotency + outbox (pattern)

## Idempotency
```
on request with Idempotency-Key K:
  if store.has(K): return store.result(K)   # no-op replay
  result = do_work()
  store.put(K, result)
```

## Outbox (write-then-publish)
```
BEGIN;
  update state ...;
  insert into outbox(event, payload);   -- same transaction
COMMIT;
-- relay polls outbox -> publishes -> marks sent
```
