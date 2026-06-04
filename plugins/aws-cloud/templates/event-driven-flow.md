# Event-driven flow (pattern)

```
producer -> EventBridge (route) -> SQS (decouple) -> consumer (idempotent)
                                          |-> DLQ (poison messages)
orchestration: Step Functions (retries + error handling)
```

- Every consumer **idempotent** (dedup key)
- Every async queue has a **DLQ** + alarm
- No hand-rolled polling/cron where EventBridge fits
