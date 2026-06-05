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

---

## Decision Tree: Which payment method type for this use case?

**When this applies:** Designing a payment integration and choosing between card, bank transfer (ACH/SEPA), digital wallet, or other payment method types. Observable triggers: "should we support ACH?"; "what payment methods do we need for EU customers?"; "can we use bank transfer for subscription renewals?"

**Last verified:** 2026-06-05 against standard payment method selection practice.

```mermaid
graph TD
  A[Choose payment method type] --> B{Is the customer in the EU or UK?}
  B -- Yes --> C{Transaction type: one-off or recurring subscription?}
  C -- One-off --> D[Card via 3DS2 - SCA required for most transactions]
  C -- Recurring --> E[Card on file with SCA exemption OR SEPA Direct Debit - verify mandate requirements]
  B -- No, primarily US --> F{Is the transaction value high - over ~1000 USD?}
  F -- High value or B2B --> G{Does the customer prefer bank transfer?}
  G -- Yes --> H[ACH Debit - slower settlement; hold fulfillment until cleared]
  G -- No --> I[Card - faster settlement; immediate fulfillment]
  F -- Standard value --> I
```

_ACH and SEPA have settlement delays; fulfillment gates on the confirmed webhook._

**Rationale per leaf:**
- *Card via 3DS2 (EU/UK one-off)* — SCA mandatory for most EU/UK card transactions; 3DS2 is the standard path.
- *Card on file / SEPA (EU/UK recurring)* — subscription renewals can use a SCA exemption for recurring charges OR SEPA Direct Debit which has its own mandate flow `[verify-at-build]`.
- *ACH debit (US high-value/B2B)* — lower interchange cost for large B2B transactions; 1-3 day settlement delay is acceptable.
- *Card (US standard)* — fastest settlement, best cardholder protection; the default for consumer transactions.

**Tradeoffs summary:**

| Method | Settlement | SCA needed | Chargeback risk | Use when |
|---|---|---|---|---|
| Card (on-session) | Instant | Yes (EU/UK) | Higher | Consumer one-off; fast settlement needed |
| Card (off-session) | Instant | SCA exemption needed | Higher | Subscription renewal; mandate in place |
| ACH debit | 1-3 days | No | Lower | High-value B2B; cost-sensitive |
| SEPA direct debit | 3-5 days | Mandate only | Lower (different dispute window) | EU recurring; bank-to-bank preferred |

---

## Decision Tree: Subscription renewal failure — which dunning path?

**When this applies:** A subscription renewal charge has failed and a dunning decision must be made. Observable triggers: a `invoice.payment_failed` or `charge.failed` webhook; a subscription moving to `past_due`; "how should we handle failed renewals?"

**Last verified:** 2026-06-05 against standard dunning practice and PSP documentation.

```mermaid
graph TD
  A[Renewal charge failed] --> B{What is the failure reason code?}
  B -- Hard decline: stolen/lost/closed/revoked/invalid --> C[Do NOT retry - request new payment method immediately]
  B -- Soft decline: NSF/issuer timeout/do-not-honor/velocity --> D{Is SCA required - EU/UK authentication_required?}
  D -- Yes --> E[Send re-authentication link - off-session SCA path; retry after re-auth]
  D -- No --> F{Retries remaining in dunning schedule?}
  F -- Yes --> G[Smart retry: space retries to paydays - not within 24h]
  F -- No --> H{Customer on annual plan - high LTV?}
  H -- Yes --> I[Escalate to manual outreach before canceling]
  H -- No --> J[Cancel subscription after dunning exhausted; offboard cleanly]
  C --> K[Email: update your card; preserve access during grace period]
  G --> L[Monitor for recovery; preserve access during grace period]
```

_A hard decline retried is a fraud signal to the card network — never retry a hard decline._

**Rationale per leaf:**
- *No retry (hard decline)* — retrying a hard decline trains the card network that this merchant abuses the network; it can result in the merchant account being flagged.
- *Re-authentication link (SCA)* — the `authentication_required` error code means the card is valid but the cardholder needs to re-authenticate; a new payment attempt requires a new SCA flow.
- *Smart retry* — soft declines are often timing-related (insufficient funds near payroll); spacing retries to likely recovery times (end of month, after payday) recovers more.
- *Manual outreach (high LTV)* — high-value annual customers warrant a human touch before cancellation; automated dunning alone is insufficient.
- *Cancel cleanly* — after dunning exhaustion, cancel with a clean offboarding flow and a "re-subscribe" path; harsh cancellation increases support tickets.

---

## Decision Tree: PCI scope assessment — which SAQ applies?

**When this applies:** Assessing the PCI-DSS scope for a payment integration. Observable triggers: "what is our PCI scope?"; "do we need a QSA assessment?"; "how do we stay on SAQ-A?"

**Last verified:** 2026-06-05 against PCI-DSS v4.0 SAQ guidance `[verify-at-build — SAQ specifics change; consult a QSA for authoritative scope assessment]`.

```mermaid
graph TD
  A[PCI scope assessment] --> B{Does your server ever receive, process, or store raw card data - PANs, CVVs, track data?}
  B -- Yes --> C[STOP: you are out of SAQ-A - escalate to security-reviewer + QSA immediately]
  B -- No --> D{Are all card data entry pages fully hosted by the PSP - no inline form on your domain?}
  D -- Yes: PSP-hosted pages redirect or iFrame --> E[SAQ-A eligible - verify the exact iFrame/redirect requirements with a QSA]
  D -- No: you serve a payment form on your domain --> F{Does your JavaScript handle any card field values?}
  F -- Yes --> G[Likely SAQ-A-EP or SAQ-D - escalate to QSA for full assessment]
  F -- No: PSP JS SDK handles fields - you never see card data in your JS --> H[SAQ-A eligible with JS controls - verify with QSA]
```

_PCI scope is a compliance verdict: this tree guides engineering design, not regulatory clearance. Always verify with a QSA._

**Rationale per leaf:**
- *Out of SAQ-A (server receives card data)* — if card numbers touch your server in any form, you are out of SAQ-A scope; QSA engagement is mandatory.
- *SAQ-A eligible (PSP-hosted pages)* — the simplest path: redirect or iFrame to the PSP's hosted page so no card data touches your domain.
- *SAQ-A-EP or SAQ-D (your JS handles fields)* — if your JavaScript can access card field values (even transiently), you carry a larger scope; QSA assesses which SAQ applies.
- *SAQ-A with JS controls (PSP SDK)* — PSP-provided JS elements (Stripe Elements, Adyen Web, etc.) inject iFrames that keep card data in the PSP's origin; your code never sees the values. SAQ-A eligible subject to QSA confirmation.

**Tradeoffs summary:**

| Integration pattern | PCI scope | Implementation complexity | Developer experience |
|---|---|---|---|
| PSP-hosted redirect page | SAQ-A (smallest) | Lowest | Lower control over UX |
| PSP JS SDK elements | SAQ-A (with controls) | Low | Good UX; card in PSP iFrame |
| Your JS form + PSP tokenize | SAQ-A-EP or higher | Medium | More UX control; larger scope |
| Server receives card data | SAQ-D or custom (largest) | High | Full control; maximum compliance cost |
