# fintech-payments-engineering — best-practice docs

Named, citable rules for the `fintech-payments-engineering` plugin's specialists. Each file is **one rule**, grounded in this plugin's domain: payment integration, subscription and usage billing, ledger/reconciliation, and PCI scope minimization.

Accounting (revenue recognition, GL) routes to `finance`. Financial regulation (money transmission, AML/KYC) routes to `regulatory-compliance`. Security verdicts route to `ravenclaude-core/security-reviewer`.

---

## Index

_22 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`double-entry-ledger-is-source-of-truth.md`](./double-entry-ledger-is-source-of-truth.md) | Absolute rule | Designing any money-movement feature |
| [`never-log-pan-or-cvv.md`](./never-log-pan-or-cvv.md) | Absolute rule | Any logging or observability around payments |
| [`every-money-operation-is-idempotent.md`](./every-money-operation-is-idempotent.md) | Absolute rule | Every charge, refund, payout, or webhook handler |
| [`money-is-integers.md`](./money-is-integers.md) | Absolute rule | Any code that stores or calculates a money amount |
| [`minimize-pci-scope-with-tokenization.md`](./minimize-pci-scope-with-tokenization.md) | Absolute rule | Designing any cardholder-data flow |
| [`reconcile-continuously.md`](./reconcile-continuously.md) | Absolute rule | Operating a live payment system |
| [`retry-soft-declines-not-hard.md`](./retry-soft-declines-not-hard.md) | Absolute rule | Building any payment retry or dunning logic |
| [`payments-engineering-route-accounting-and-regulation.md`](./payments-engineering-route-accounting-and-regulation.md) | Absolute rule | Any time the topic crosses into accounting or regulation |
| [`handle-3ds-sca-and-declines.md`](./handle-3ds-sca-and-declines.md) | Absolute rule | Integrating card payments for EU/UK customers |
| [`model-the-charge-as-a-state-machine.md`](./model-the-charge-as-a-state-machine.md) | Absolute rule | Designing a charge or payment intent flow |
| [`verify-and-dedupe-webhooks.md`](./verify-and-dedupe-webhooks.md) | Absolute rule | Implementing any PSP webhook handler |
| [`dunning-without-churning.md`](./dunning-without-churning.md) | Pattern | Designing failed-payment recovery for subscriptions |
| [`subscription-as-a-state-machine.md`](./subscription-as-a-state-machine.md) | Absolute rule | Designing any recurring billing feature |
| [`proration-calculate-then-confirm.md`](./proration-calculate-then-confirm.md) | Pattern | Implementing plan changes mid-billing-cycle |
| [`outbox-pattern-for-payment-events.md`](./outbox-pattern-for-payment-events.md) | Pattern | Building reliable payment event delivery to downstream systems |
| [`multi-currency-store-base-and-presentational.md`](./multi-currency-store-base-and-presentational.md) | Absolute rule | Any payment feature serving multiple currencies |
| [`dispute-evidence-before-deadline.md`](./dispute-evidence-before-deadline.md) | Absolute rule | Operating a live payment system that accepts disputes |
| [`usage-metering-buffer-then-batch.md`](./usage-metering-buffer-then-batch.md) | Pattern | Building usage-based billing or metering |
| [`payment-method-lifecycle.md`](./payment-method-lifecycle.md) | Pattern | Building stored payment method or subscription renewal flows |
| [`invoice-is-idempotent-and-immutable.md`](./invoice-is-idempotent-and-immutable.md) | Absolute rule | Building invoicing for subscriptions or usage billing |
| [`ach-bank-transfer-settlement-delay.md`](./ach-bank-transfer-settlement-delay.md) | Absolute rule | Integrating ACH or SEPA bank transfer payments |
| [`sca-orchestrate-server-side.md`](./sca-orchestrate-server-side.md) | Absolute rule | Building SCA/3DS flows for EU/UK card payments |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution and house opinions
- [`../knowledge/fintech-payments-engineering-decision-trees.md`](../knowledge/fintech-payments-engineering-decision-trees.md) — decision trees the agents traverse
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs
