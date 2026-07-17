# subscription-billing-revenue

> The **subscription billing system layer** for Claude Code — the engineering team that turns a price into a *recurring invoice, a collection, and recognized revenue*, and builds the system that does it. Two agents: the **billing-systems-architect** (designs the plan/catalog model, proration & lifecycle rules, build-vs-buy & platform selection, entitlement & metering/rating design, and the ASC 606 rev-rec architecture) and the **billing-implementation-engineer** (integrates the provider, handles webhooks with idempotency & reconciliation, writes lifecycle & dunning code, builds the usage-metering pipeline and the MRR/rev-rec reporting).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

> **Not accounting, tax, or audit advice.** ASC 606 revenue-recognition treatment and sales-tax/VAT rules are volatile and entity-specific — carry a retrieval date, verify at use, and confirm with a qualified accountant/auditor before booking.

## What it does

| You ask | It returns |
|---|---|
| "Model our subscription plans and product catalog." | A plan/catalog model (product vs price vs plan vs entitlement) expressing flat/tiered/per-seat/usage/hybrid, with the proration & lifecycle rules — and why a wrong plan model is a migration, not a config change |
| "Build billing in-house or use Stripe Billing / Chargebee / Zuora / Recurly / Metronome?" | A build-vs-buy recommendation and a provider-neutral platform pick tied to catalog complexity, metering, tax/invoicing, and rev-rec — with the migration cost and flip conditions |
| "How should entitlements / feature-gating work?" | An entitlement architecture (source of truth, propagation, enforcement point) derived from subscription state and fail-closed |
| "Integrate the provider and handle the subscription webhooks safely." | A provider integration plus an idempotent at-least-once webhook handler (dedup key + event log) and a reconciliation job that repairs drift |
| "Payments are failing — build our dunning and recover the revenue." | A dunning implementation: decline-reason-tuned smart retries + card-updater, a customer sequence, grace-period & entitlement downgrade, and recovery instrumentation |
| "Build our usage metering so the invoice matches what customers used." | An idempotent, auditable metering/rating pipeline that reconciles every invoice line to its metered events, with late-event & correction handling |
| "Recognize revenue per ASC 606 and build MRR/ARR/churn reporting." | A rev-rec build: the ASC 606 five-step mapping, a deferred-revenue schedule, and MRR/ARR movement + NRR/churn — with billing kept cleanly separate from rev-rec (accountant-verified) |

**Two rules it never breaks:** *every webhook is at-least-once* (idempotency and reconciliation are non-negotiable — assume duplicate, out-of-order, and dropped events), and *revenue recognized ≠ cash collected* (keep the billing and rev-rec ledgers separate; usage metering must be idempotent, auditable, and reconcilable to the invoice).

## What's inside

- **2 agents** — `billing-systems-architect` (designs the plan/catalog model, proration & lifecycle, build-vs-buy & platform selection, entitlement architecture, metering/rating design, and the ASC 606 rev-rec architecture) and `billing-implementation-engineer` (integrates the billing provider, handles webhooks with idempotency & reconciliation, writes subscription-lifecycle & dunning code, builds the usage-metering pipeline, enforces entitlements, and builds the rev-rec/MRR reporting).
- **3 skills** — `design-billing-model-and-catalog`, `build-billing-integration-and-dunning`, `implement-usage-metering-and-revrec`.
- **2 knowledge files** — a Mermaid billing decision tree (catalog modeling, build-vs-buy, webhook idempotency, dunning, metering→rating→invoice→rev-rec + trade-off tables) and a 2026 billing-patterns reference (the four-concept catalog model, proration & lifecycle, at-least-once webhooks, dunning, usage metering, ASC 606 rev-rec, SaaS metrics, tax, and a dated standards/provider map).
- **2 templates** — a billing model design doc and a rev-rec & dunning runbook.

## Where it sits in the revenue stack

```
subscription-billing-revenue (HERE)  →  the BILLING SYSTEM              ("turn a price into a recurring invoice, a collection, and recognized revenue")
pricing-monetization                 →  pricing STRATEGY & packaging     ("what to charge")
fintech-payments-engineering         →  payment RAILS / PSP / ledger code ("moving the money")
finance                              →  FP&A / budgeting / the P&L plan   ("the earnings plan")
analytics-engineering                →  the warehouse / transform pipeline ("MRR/ARR/churn at scale")
```

This plugin is the **subscription billing system**: it turns a price into a **recurring invoice**, a **collection**, and **recognized revenue** — and stays clear of the *pricing strategy* (`pricing-monetization`), the *payment rails* (`fintech-payments-engineering`), and the *FP&A plan* (`finance`).

## Domain stance

Concept-first (model the catalog before the integration; product vs price vs plan vs entitlement; proration & lifecycle as data-shaped rules; build-vs-buy on coverage; at-least-once webhooks with idempotency & reconciliation; decline-reason-tuned dunning as measured recovery; idempotent + reconcilable usage metering; deterministic rating; billing separate from rev-rec), fluent across **flat / tiered (graduated vs volume) / per-seat / usage / hybrid** packaging, **Stripe Billing / Chargebee / Zuora / Recurly / Metronome** (provider-neutral), **entitlements & feature-gating**, the **event ingestion → dedup → aggregation → rating → invoice → reconciliation** pipeline, the **ASC 606 five-step** with **deferred revenue**, and **MRR/ARR/NRR/churn**. ASC 606 treatment, sales-tax/VAT rules, and provider APIs carry retrieval dates — re-verify (and confirm with a qualified accountant) before pinning in a deliverable or booking. **Not accounting, tax, or audit advice.**

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install subscription-billing-revenue@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
