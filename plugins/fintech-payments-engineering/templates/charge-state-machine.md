# Charge state machine

```
created -> requires_action (3DS/SCA) -> processing -> succeeded
                                                  \-> failed (hard: stop / soft: dunning retry)
succeeded -> refunded (full/partial)
succeeded -> disputed -> won/lost
```

- Every transition idempotent; driven by VERIFIED webhooks.
- Idempotency key on create/refund. State is explicit, not inferred from flags.
