# Make async consumers idempotent and give them a DLQ

Every SQS/SNS/EventBridge consumer must be idempotent (retries are guaranteed) and have a dead-letter queue (poison messages must not block the queue or vanish). Retries without idempotency corrupt data; retries without a DLQ silently lose it. These two together are the difference between a robust event system and a data-integrity incident.
