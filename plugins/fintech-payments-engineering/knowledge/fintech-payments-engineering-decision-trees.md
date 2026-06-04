# Fintech & Payments — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before building a charge flow or assessing PCI scope. Accounting -> finance, regulation -> regulatory-compliance, verdict -> security-reviewer.

## Decision Tree: Charge flow correctness

Make money move exactly once, driven by verified webhooks.

```mermaid
graph TD
  A[Initiating a charge] --> B{Idempotency key set?}
  B -- No --> C[STOP: add it - a retry double-bills]
  B -- Yes --> D{Needs SCA/3DS?}
  D -- Yes --> E[requires_action: client confirmation step normal]
  D -- No --> F[Confirm charge]
  E --> F
  F --> G{Drive final state from a VERIFIED webhook?}
  G -- No --> H[Don't trust only the sync response; webhooks are the source of truth]
  G -- Yes --> I{Webhook signature verified + deduped by event id?}
  I -- No --> J[Unverified/duplicate = spoof/double-post risk]
  I -- Yes --> K[Post to the double-entry ledger; reconcile to PSP]
```

_Every money op idempotent; the ledger (not the PSP) is your source of truth._

## Decision Tree: PCI scope: which SAQ?

Architecture determines scope; tokenization is the dominant strategy.

```mermaid
graph TD
  A[Handling payments] --> B{Does the raw PAN ever touch YOUR servers?}
  B -- No, PSP client-side tokenization --> C[SAQ-A: minimal scope - the goal]
  B -- Your page, PSP iframe/redirect --> D[SAQ-A-EP: your page in scope]
  B -- Yes, you receive/transmit PAN --> E[SAQ-D: full scope - heavy; re-architect to tokenize]
  C --> F[Log money ops, never card data; route attestation to regulatory-compliance/legal]
  D --> F
  E --> F
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Stripe/Adyen/Braintree intents + tokenization | GA | Client-side elements -> SAQ-A |
| Idempotency keys (PSP-supported) | GA | On every money op |
| Webhook signing | GA | Verify; handle idempotently |
| 3DS2 / SCA | in force (esp. EU) | requires_action is normal |
| PCI-DSS v4.0 | in force | v3.2.1 retired; verify SAQ specifics |
| Double-entry ledger pattern | established | Source of truth, reconcile to PSP |
