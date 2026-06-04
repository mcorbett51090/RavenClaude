# Make every money operation idempotent

Attach an idempotency key to every charge, refund, and payout, and dedupe webhook handlers by event id. Networks, load balancers, and the PSP itself all retry, and a non-idempotent money operation that gets retried double-charges the customer — the single most damaging and most common payments bug. Idempotency is the structural defense that makes double-billing impossible rather than merely unlikely.
