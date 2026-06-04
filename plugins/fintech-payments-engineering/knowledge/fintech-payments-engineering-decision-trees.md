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

## Decision Tree: Retry or stop after a decline?

Branch on the decline category from the issuer reason code; never blanket-retry.

```mermaid
graph TD
  A[Charge declined] --> B{Decline category from the reason code?}
  B -- Hard: stolen/lost/invalid/closed/revoked --> C[STOP - retrying abuses network signals; ask for a new method]
  B -- Soft: insufficient funds/issuer timeout/velocity/do-not-honor --> D{Retryable budget left?}
  D -- No --> E[Stop retrying; prompt customer / dunning comms]
  D -- Yes --> F{Subscription vs one-off?}
  F -- Subscription --> G[Smart retry on a schedule timed to paydays/bank behavior]
  F -- One-off --> H[Retry with backoff, small cap, then prompt for action]
  C --> I[Surface a clear, actionable message - recover the conversion]
```

_Map every reason code to hard-or-soft up front; guessing turns a recoverable failure into a network-flagged merchant account._

## Decision Tree: Reconciliation discrepancy triage

A non-zero difference is a defect with an owner until proven otherwise — never written off.

```mermaid
graph TD
  A[Ledger != PSP report] --> B{PSP has a charge your ledger is missing?}
  B -- Yes --> C[Likely a dropped/unprocessed webhook - replay it, post the entry]
  B -- No --> D{Ledger has an entry with no PSP counterpart?}
  D -- Yes --> E[Phantom credit/double-post - investigate idempotency + dedupe]
  D -- No --> F{Amounts differ on a matched pair?}
  F -- Yes --> G{Explained by fees/FX/partial capture?}
  G -- Yes --> H[Model the fee/FX/partial in the ledger; re-match]
  G -- No --> I[Escalate - unexplained money delta = bug or fraud]
  F -- No --> J[Timing only - resolves next cycle; track, don't ignore]
```

_The longer a discrepancy sits, the more entries pile on the error. Mystery money is a bug or a breach until shown otherwise._

## Decision Tree: Refund, dispute, or chargeback path?

Each is a distinct state-machine transition driven by verified webhooks, posted to the ledger.

```mermaid
graph TD
  A[Money needs to come back / is contested] --> B{Initiated by you or the customer's bank?}
  B -- You merchant-initiated --> C{Full or partial?}
  C -- Full --> D[Refund via PSP w/ idempotency key; reverse the ledger entry]
  C -- Partial --> E[Partial refund; post the partial reversal, keep the remainder]
  B -- Bank: chargeback/dispute --> F{Evidence to contest?}
  F -- Yes --> G[Submit evidence by the deadline; ledger holds disputed state]
  F -- No --> H[Accept; post the reversal + dispute fee to the ledger]
  D --> I[Drive final state from the VERIFIED webhook, not the sync call]
  E --> I
  G --> I
```

_A late refund or a chargeback arriving weeks after success is why the charge must be a state machine, not a paid boolean._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Stripe/Adyen/Braintree intents + tokenization | GA | Client-side elements -> SAQ-A |
| Idempotency keys (PSP-supported) | GA | On every money op |
| Webhook signing | GA | Verify; handle idempotently |
| 3DS2 / SCA | in force (esp. EU) | requires_action is normal |
| PCI-DSS v4.0 | in force | v3.2.1 retired; verify SAQ specifics |
| Double-entry ledger pattern | established | Source of truth, reconcile to PSP |
