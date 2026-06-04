# Stream processing job (pattern)

```
source(orders)
  .assignTimestampsAndWatermarks(eventTime, watermark = maxOutOfOrderness)
  .keyBy(order_id)
  .window(Tumbling(5 min))
  .allowedLateness(2 min)            // + side output for stragglers
  .aggregate(...)                    // checkpointed state, TTL-bounded
  .sink(idempotent / transactional)
```
Monitor consumer lag -> observability-sre.
