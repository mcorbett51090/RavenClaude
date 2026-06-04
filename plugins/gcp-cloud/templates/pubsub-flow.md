# Pub/Sub event flow (pattern)

```
publisher -> Topic -> Subscription -> consumer (idempotent)
                          |-> Dead-letter Topic (poison messages)
```

- Consumers **idempotent** (dedup key)
- **Dead-letter topic** + alert on every subscription
- Ack deadline tuned; no hand-rolled polling
