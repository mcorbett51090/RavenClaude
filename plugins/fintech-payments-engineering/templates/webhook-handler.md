# Webhook handler (pattern)

```
on webhook:
  verify signature (reject if invalid)        # untrusted public endpoint
  if seen(event.id): return 200                # idempotent: dedupe
  record(event.id)
  apply(event) to the charge state machine     # tolerate out-of-order
  post to ledger (idempotent)
  return 200
```
Webhooks are at-least-once + out-of-order; never log PAN/CVV.
