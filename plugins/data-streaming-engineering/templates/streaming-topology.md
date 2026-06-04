# Streaming topology

```
[DB] --Debezium CDC--> [orders topic (key=order_id, 12 parts)] --> [Flink: event-time window + watermark] --> [sink (exactly-once / idempotent)]
```

| Hop | Delivery semantic | Ordering | State |
|---|---|---|---|
| CDC -> topic | at-least-once | per order_id | — |
| topic -> processor | at-least-once + idempotent | per partition | checkpointed, TTL |
| processor -> sink | <exactly-once if sink supports / else dedup> | — | — |

_Batch alternative considered? <yes/no + why streaming>_
