---
name: build-billing-integration-and-dunning
description: "Build the billing-provider integration and the failed-payment recovery by traversing the build path (provider integration → webhook handling with idempotency & reconciliation → subscription lifecycle: trials/plan-changes/proration/cancellation → invoicing/tax/coupons → dunning & smart-retry → grace-period & entitlement downgrade), then return the integration, an idempotent at-least-once webhook handler, a reconciliation job, the lifecycle code, and an instrumented dunning flow. Reach for this when the user asks 'integrate Stripe Billing / Chargebee', 'handle subscription webhooks without double-processing', 'build our dunning/retry', or 'recover failed payments'. Every webhook is at-least-once — idempotency and reconciliation are non-negotiable. Used by billing-implementation-engineer (primary) and billing-systems-architect."
---

# Skill: build-billing-integration-and-dunning

> **Invoked by:** `billing-implementation-engineer` (primary — the integration, webhooks, lifecycle, and dunning build) and `billing-systems-architect` (to ground the design in what integration/dunning actually require).
>
> **When to invoke:** "integrate Stripe Billing / Chargebee / Recurly / Zuora"; "handle the subscription webhooks idempotently"; "build our subscription lifecycle (trials / plan changes / proration / cancellation)"; "build dunning / smart retries / failed-payment recovery"; any "wire up the billing provider and recover failed payments" question.
>
> **Output:** the provider integration + an idempotent at-least-once webhook handler + a reconciliation job + the subscription-lifecycle code + an instrumented dunning/retry flow with grace-period & entitlement downgrade.

## Procedure

1. **Integrate against the model, not around it.** Confirm the plan/catalog + entitlement model (from [`design-billing-model-and-catalog`](../design-billing-model-and-catalog/SKILL.md)) before writing integration. Build the core flows: subscription **create / update / cancel**, invoice retrieval, tax and coupon application. If a needed packaging shape or proration case isn't in the model, kick it back to the architect — don't reshape the model in integration code.
2. **Treat every webhook as at-least-once — idempotency is non-negotiable.** Providers deliver **duplicate, out-of-order, and occasionally dropped** events. For each handler: derive a **dedup key** (the provider event id), persist an **event log**, and make application a **no-op on replay**. Never blindly apply deltas from a possibly-stale event — reconcile to the provider's current object state. Traverse the webhook branch in [`../../knowledge/subscription-billing-revenue-decision-tree.md`](../../knowledge/subscription-billing-revenue-decision-tree.md).
3. **Add a reconciliation job — silent drift is lost revenue.** On a schedule, pull provider state (subscriptions, invoices, payments) and **compare to your ledger**; repair drift (a missed cancellation, a webhook never delivered, an out-of-order status). Alert when drift is non-zero. The reconciliation job is the backstop that makes at-least-once webhooks safe; treat webhook-vs-provider drift = 0 as the health metric.
4. **Build the subscription lifecycle deliberately.** Implement **trials** (with/without card, trial→paid conversion), **plan changes** (upgrade now with proration; downgrade at period end), **quantity/seat** proration, **coupon/discount** application and expiry, and **cancellation** (immediate vs end-of-period) + reactivation — matching the architect's proration rules. Verify proration math against the provider's, don't reinvent it.
5. **Build dunning as a measured recovery system, not a cron that retries.** Design the **smart retry schedule** — retry timing tuned to the **decline reason** (soft declines like insufficient funds retry on a schedule; hard declines like "lost card" don't), integrate the card **account-updater**, and cap attempts. Layer the **customer sequence** (dunning emails / in-app prompts to update the card), a **grace period**, and on final failure the **entitlement downgrade** (fail closed). Dunning recovers more revenue than any pricing tweak — so **instrument it**: recovery rate per retry, involuntary-churn rate, revenue recovered.
6. **Make invoicing and tax the provider's job where possible.** Prefer the provider's invoicing, tax (sales-tax/VAT) engine, and PCI-scoped card handling over rebuilding them — that coverage is why you bought the platform. Handle invoice finalization, payment, and failure webhooks idempotently per step 2.
7. **Prove it with a reconciliation/audit loop.** End with the evidence: webhook-vs-provider **drift = 0**, a replayed webhook is a **no-op**, the dunning **recovery rate**, and the entitlement state correctly **fails closed** on final non-payment. Route rail/PSP/ledger code to `fintech-payments-engineering`; deep tax logic beyond the provider to the accountant.

## Worked example

> User: "We integrated Stripe Billing but occasionally double-count a cancellation and our failed payments just churn. Fix both."

- **Idempotency:** the `customer.subscription.deleted` handler applied a delta each delivery → add a **dedup key** on the Stripe event id + an **event log**; make cancellation **idempotent** (set status to canceled, not decrement). A replay is now a no-op.
- **Out-of-order:** a late `updated` arriving after `deleted` re-activated the sub → **reconcile to Stripe's current object** instead of applying the event's snapshot.
- **Reconciliation job:** nightly, pull Stripe subscriptions and compare to the ledger; repair any status drift; alert if drift ≠ 0.
- **Dunning:** replace the blind 3× daily retry with a **decline-reason-tuned** schedule (soft declines retried over days; hard declines stop), enable the **card account-updater**, add a **dunning email sequence** + a 7-day **grace period**, and **downgrade entitlements** (fail closed) on final failure.
- **Instrumentation:** track recovery rate per retry and involuntary-churn rate → the recovery flow is now measured, and the double-count is gone.

## Guardrails

- **Every webhook is at-least-once** — dedup key + event log + no-op-on-replay is mandatory; never assume exactly-once.
- **Reconcile to provider state, don't apply stale deltas** — out-of-order events must not corrupt subscription status.
- **Run a reconciliation job** — silent provider-vs-ledger drift is lost revenue; drift = 0 is the health metric.
- **Dunning is a measured recovery system** — tune retries to the decline reason, use the card account-updater, and instrument the recovery rate; a blind retry loop leaves involuntary churn on the table.
- **On final non-payment, downgrade entitlements fail-closed** — a non-paying customer must not keep paid access.
- **Prefer the provider's invoicing / tax / PCI handling** — that coverage is what you bought; don't rebuild it.
- Integration/dunning is **execution** (the `billing-implementation-engineer` owns it); the model/proration rules are **architecture** (`billing-systems-architect`) — keep the seam clean.
- This is **not** payment-rail/PSP/ledger code (that's `fintech-payments-engineering`), and **not accounting or tax advice** — provider webhook payloads and tax rules are volatile, carry a **retrieval date**. See [`../../knowledge/subscription-billing-revenue-patterns-2026.md`](../../knowledge/subscription-billing-revenue-patterns-2026.md).
