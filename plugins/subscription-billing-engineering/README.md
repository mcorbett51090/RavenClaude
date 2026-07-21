# subscription-billing-engineering

The **recurring-billing system layer** for SaaS — the "money plumbing" that `pricing-monetization` (strategy) and `fintech-payments-engineering` (payment rails) both punt on. Two specialist agents design and build the plan/price/entitlement model, proration, usage metering, dunning, and idempotent webhook reconciliation, with clean seams to revenue recognition and tax.

## What's inside

| Component | Items |
|---|---|
| Agents | 2 — `billing-systems-architect`, `billing-implementation-engineer` |
| Skills | 3 — `model-plans-and-pricing`, `implement-metered-billing`, `design-dunning-and-recovery` |
| Knowledge | 2 — billing-model decision tree, webhooks-idempotency & revrec |
| Templates | 2 — billing-integration runbook, proration-upgrade test matrix |

## When to use it

- **"Which billing model fits us — flat, tiered, per-seat, usage, or hybrid?"** → `billing-systems-architect`
- **"How do we prorate a mid-cycle upgrade correctly?"** → `billing-systems-architect` (+ the proration test matrix)
- **"Is our Stripe webhook handling actually idempotent and reconciled?"** → `billing-systems-architect` audit → `billing-implementation-engineer` fix
- **"Integrate Stripe Billing / implement usage billing / wire entitlements."** → `billing-implementation-engineer`
- **"Reduce involuntary churn from failed payments."** → `design-dunning-and-recovery`

## House line

**Model before you integrate; idempotency before features.** A wrong billing model re-prices every customer to fix; a non-idempotent webhook double-charges them. The provider is the source of truth — your database is a cache that reconciles to it.

## Seams (what this plugin does NOT own)

| Need | Route to |
|---|---|
| Payment rails (auth/capture, PSP, PCI, SCA/3DS) | `fintech-payments-engineering` |
| Pricing/packaging strategy, willingness-to-pay | `pricing-monetization` |
| Revenue recognition (ASC 606), deferred revenue | `finance` |
| Sales-tax / VAT / GST by jurisdiction | `regulatory-compliance` |
| Subscription/usage schema + migrations | `database-engineering` |
| Email deliverability for dunning comms | `email-engineering` |

## Requirements

Requires `ravenclaude-core@>=0.7.0` (inherits the Capability Grounding Protocol, Structured Output Protocol, and the domain-neutral team roster).

## Install

```
/plugin marketplace update ravenclaude
/plugin install subscription-billing-engineering@ravenclaude
```

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (roster, routing, house opinions, output contract).
