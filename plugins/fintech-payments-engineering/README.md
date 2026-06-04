# Fintech & Payments Engineering

The **fintech-payments-engineering** plugin — building payment and billing systems correctly — payment integration (Stripe-style), subscription/usage billing, money-safe ledgers and reconciliation, and PCI scope minimization — the engineering, with financial-regulatory and accounting routed out.

## Agents

- **`payments-architect`** — Payment system architecture: PSP/processor choice, money representation (integer minor units, multi-currency), the double-entry ledger as source of truth, reconciliation design, and the payment-flow topology
- **`payments-integration-engineer`** — PSP integration: payment intents/charges with idempotency keys, webhook signature verification + idempotent handling, 3DS/SCA, saved payment methods, refunds, retries and failure handling, and the charge state machine
- **`billing-subscriptions-engineer`** — Subscription and usage billing: plans and pricing models, proration, usage metering, invoicing, the billing cycle, dunning/failed-payment recovery, and emitting clean revenue events for finance
- **`payments-pci-compliance-advisor`** — PCI-DSS scope minimization (the engineering posture): tokenization so card data never touches your servers, SAQ-A posture, secure handling of payment data, audit/logging of money operations, and routing the regulatory + verdict questions out

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install fintech-payments-engineering@ravenclaude
```

## Seams

- **Revenue recognition (ASC 606), GL postings, the chart of accounts, financial close** → `finance`; this team produces the money events and ledger, that team does the accounting on top.
- **Financial-services regulation (money transmission, AML/KYC, licensing, regulator reporting)** → `regulatory-compliance`; we build the payment mechanics, not the regulatory compliance.
- **The security verdict on a PCI/payment-flow finding** → `ravenclaude-core/security-reviewer` (via `security-engineering`); we minimize scope and recommend, they clear it.
- **The API contract for our payment endpoints + webhook semantics** → `api-engineering`; the service implementation behind it → `backend-engineering` (idempotency/outbox).
- **End-user authentication around payments / stored-credential consent UX** → `auth-identity`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
