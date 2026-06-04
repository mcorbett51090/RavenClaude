# Make every retried operation idempotent

Webhooks, payment calls, message consumers, and any retried request must carry an idempotency/dedup key so a duplicate delivery is a no-op rather than a double-effect. Retries are guaranteed by networks, load balancers, and queues; a non-idempotent operation that gets retried double-charges, double-ships, or double-writes. Idempotency is not optional in a distributed system.
