# Knowledge — Subscription-billing-revenue patterns (2026)

> **Last reviewed:** 2026-07-17 · **Confidence:** High on the durable concepts (the product/price/plan/entitlement catalog model, proration & lifecycle, at-least-once webhooks & idempotency, dunning, usage metering & rating, billing-vs-rev-rec separation, MRR/ARR/NRR); **Medium on the dated regulatory/standard/provider map — ASC 606 mechanics, sales-tax/VAT rules, and billing-provider APIs change and carry retrieval dates below.**
> The reference the `billing-implementation-engineer` reads when integrating the provider, handling webhooks, building dunning, metering usage, and building rev-rec/reporting — plus a 2026 standards/tooling snapshot. **This is not accounting, tax, or audit advice; volatile specifics carry a retrieval date and are verified at use.**

The team's discipline: **model the catalog before the integration; treat every webhook as at-least-once and reconcile; meter idempotently and reconcilably to the invoice; instrument dunning; and keep billing separate from revenue recognition.**

---

## The plan & product catalog model — the four concepts

The single most consequential model in a billing system. Keep these **separate**:

| Concept | What it is | Kept separate because |
|---|---|---|
| **Product** | The sellable thing (the app, a module, an add-on) | Its identity is stable while pricing churns |
| **Price** | How it's charged — amount, interval, currency, tier/usage rules | You re-price constantly; it must move without touching the product |
| **Plan / Subscription** | What a specific customer holds — the price(s), quantity, status, dates | It's per-customer state, not catalog |
| **Entitlement** | What the subscription lets the customer *use* — features, limits, meters | Enforcement is a function of subscription state, derived and fail-closed |

Collapsing price into product, or entitlement into plan, is the mistake that turns a packaging change into a **data migration**. A wrong plan model is a migration, not a config change — model it first.

**Packaging shapes:** flat (fixed/period), per-seat (price × quantity), tiered (**graduated** — each unit in its tier; vs **volume** — all units at the reached tier), usage-based (units × rate), and **hybrid** (platform fee + usage, or seats + overage). Most real systems are hybrid — design for it from the start.

---

## Proration & subscription lifecycle

- **Plan changes** — **upgrades apply now** (prorate: credit the unused portion, charge the new plan's remainder); **downgrades usually at period end** (avoid cash refunds and gaming). Verify the proration math against the provider's rather than reinventing it.
- **Quantity/seat changes** — per-seat add = immediate proration; seat removal = credit (often at period end).
- **Trials** — with or without a card; the **trial→paid** conversion is a lifecycle event (start metering usage at conversion).
- **Coupons/discounts** — define stacking, expiry, and whether they apply to base vs usage; keep them a price-layer concept, not baked into the product.
- **Cancellation** — immediate vs end-of-period; support reactivation. Cancellation is the webhook most often mishandled (see idempotency below).

---

## Webhooks, idempotency & reconciliation — every event is at-least-once

Billing providers deliver **duplicate, out-of-order, and occasionally dropped** webhooks. This is the defining reliability property of a billing integration.

- **Idempotency** — derive a **dedup key** (the provider event id), persist an **event log**, and make every handler a **no-op on replay**. Never decrement/apply a delta per delivery — set absolute state.
- **Out-of-order tolerance** — a late event must not overwrite newer state; **reconcile to the provider's current object** rather than blindly applying the event's snapshot.
- **Reconciliation job** — on a schedule, **pull provider state** (subscriptions, invoices, payments) and compare to your ledger; **repair drift** and alert when drift ≠ 0. This is the backstop that makes at-least-once safe. Treat **provider-vs-ledger drift = 0** as the health metric — silent drift is lost revenue.

---

## Dunning & failed-payment recovery — the highest-ROI billing work

Involuntary churn (failed payments, not cancellations) is recoverable revenue. **Dunning recovers more revenue than almost any pricing tweak** — so instrument it.

- **Smart retries** — tune retry timing to the **decline reason**: soft declines (insufficient funds, temporary) retry on a schedule; hard declines (lost/stolen/closed card) don't retry — prompt a new card. Integrate the **card account-updater** (network updater) so expired/rotated cards refresh automatically.
- **Customer sequence** — dunning emails / in-app prompts to update the payment method, escalating over a **grace period**.
- **Entitlement downgrade** — on final failure, **fail closed**: downgrade/suspend access so a non-paying customer doesn't keep paid features.
- **Instrumentation** — recovery rate per retry, involuntary-churn rate, revenue recovered. Recovery you don't measure is revenue you leave on the table.

---

## Usage metering & rating

The pipeline: **event ingestion → dedup → aggregation → rating → invoice line → reconciliation.**

- **Idempotent ingestion** — every usage event has an **idempotency key**; **dedup** at the door so a replay/double-send can't double-bill. Persist **raw events** as the audit trail.
- **Replay-safe aggregation** — aggregate into billing-period windows; handle **late-arriving** events and **corrections** via **correction events** (a reversal/restatement), not silent overwrites — so a re-run reproduces the number.
- **Deterministic rating** — apply the price (tiered graduated/volume, per-unit, **included pool + overage**) to the aggregate; **pin the price version** so a mid-period change doesn't re-rate history. Same events + same price = same charge.
- **Reconciliation to the invoice** — every invoice usage line **ties back** to its deduped events and rating; the total reconciles to rated usage. **An un-reconcilable meter makes the bill a guess** — build the reconciliation as a first-class artifact.

---

## Entitlements & feature-gating

- **Derived state** — entitlements are a **function of the current subscription/plan**, not a hand-maintained side table. When the subscription changes, entitlements change.
- **Source of truth** — the billing system or a dedicated entitlements service; decide and keep it single.
- **Propagation** — on subscription events (event-driven) or pulled at check time; cache carefully with an invalidation on change.
- **Enforcement & fail-closed** — enforce at a clear point (gateway / app / feature flag); an unknown or stale entitlement **denies** access rather than granting it.

---

## Revenue recognition (ASC 606) — separate from billing

**Revenue recognized ≠ cash collected.** Billing (what you invoiced/collected) and rev-rec (what you've earned) are **separate ledgers**; deferred revenue is the bridge.

**The ASC 606 five-step model** (durable concept; treatment is accountant territory):

1. **Identify the contract** with the customer.
2. **Identify the performance obligations** (distinct goods/services — e.g. subscription access, usage, an implementation service).
3. **Determine the transaction price** (including variable consideration like usage/overage).
4. **Allocate** the transaction price to the obligations (standalone selling prices).
5. **Recognize revenue** as each obligation is satisfied — subscription access ratably over the period; **usage as consumed**.

- **Deferred revenue** — bill up front, recognize over the service period; the deferred-revenue schedule is the tie-out between billing and recognized revenue.
- **Separation** — keep the billing ledger and the rev-rec ledger distinct so neither corrupts the other.

> **Volatile + not accounting advice:** ASC 606 (and IFRS 15) mechanics — obligation identification, variable-consideration constraints, multi-element allocation — are nuanced and **entity-specific**. Treat the above as durable concepts and **confirm the treatment with a qualified accountant/auditor before booking.** _(Retrieved 2026-07-17.)_

---

## SaaS revenue metrics

| Metric | Definition | Watch out for |
|---|---|---|
| **MRR / ARR** | Normalized monthly/annual recurring revenue run-rate | A billing metric, not recognized revenue; **usage MRR** needs an explicit normalization (trailing/expected) |
| **MRR movement** | New + Expansion − Contraction − Churn | Decompose it — a flat MRR can hide high churn masked by new sales |
| **Gross vs net churn** | Gross = lost MRR; net = lost − expansion | State which; net can be negative (good) with strong expansion |
| **Net revenue retention (NRR)** | Revenue from the existing base over time (expansion − contraction − churn) | Definition varies across companies — **state yours**; the headline SaaS-health metric |
| **Deferred revenue / recognized revenue** | Billed-not-yet-earned / earned per ASC 606 | The rev-rec side; ≠ MRR and ≠ cash — accountant-verified |

---

## Tax on subscriptions (provider-mediated — volatile)

- **Sales tax (US)** — economic nexus varies by state/threshold; SaaS taxability differs by jurisdiction. Prefer the **provider's / a tax engine's** calculation over hand-rolling it.
- **VAT/GST (intl)** — place-of-supply rules, B2B reverse-charge, digital-services thresholds. Again, a tax engine (or the billing provider's tax product) owns the calculation.
- **Not tax advice** — taxability and nexus are entity- and jurisdiction-specific and change; carry a **retrieval date** and confirm with a tax professional. _(Retrieved 2026-07-17.)_

---

## 2026 standards & tooling map (dated — volatile, re-verify before quoting)

- **Billing platforms (provider-neutral categories):** subscription engines (Stripe Billing, Chargebee, Recurly), enterprise/complex-catalog + rev-rec (Zuora), usage-metering-native (Metronome and metering layers). Pick on catalog complexity, metering needs, tax/invoicing coverage, and rev-rec support — not brand. _(Retrieved 2026-07-17; provider capabilities change.)_
- **Revenue-recognition standards:** **ASC 606** (US GAAP) / **IFRS 15** — five-step, performance obligations, deferred revenue. **Not accounting advice; confirm with a qualified accountant.** _(Retrieved 2026-07-17.)_
- **Tax:** provider tax products / dedicated tax engines for US sales tax (economic nexus) and intl VAT/GST. **Not tax advice.** _(Retrieved 2026-07-17.)_
- **Webhook/idempotency:** at-least-once delivery is the norm across providers; idempotency keys + event logs + reconciliation are the durable pattern. _(Retrieved 2026-07-17.)_
- **Metering:** idempotency-keyed event ingestion, replay-safe aggregation, deterministic rating, and invoice reconciliation — the durable pattern regardless of tool. _(Retrieved 2026-07-17.)_

---

## Provenance

- Durable concepts (the product/price/plan/entitlement catalog model, packaging shapes, proration & lifecycle, at-least-once webhooks + idempotency + reconciliation, decline-reason-tuned dunning + card account-updater, idempotent + reconcilable usage metering, deterministic rating with pinned prices, derived fail-closed entitlements, billing-vs-rev-rec separation, the ASC 606 five-step, deferred revenue, MRR/ARR/NRR/churn) are consensus subscription-billing engineering practice reviewed 2026-07-17 — **High confidence**.
- The regulatory/standard/provider map — ASC 606 / IFRS 15 mechanics, US sales-tax nexus & intl VAT/GST rules, and billing-provider (Stripe Billing, Chargebee, Zuora, Recurly, Metronome) APIs/webhooks/capabilities — is a **2026-07 snapshot**; these are volatile and entity-specific, carry the retrieval dates above, and are **not accounting/tax/audit advice** — re-verify with `ravenclaude-core/deep-researcher` and a qualified accountant/auditor before pinning in a deliverable or booking. _(Reviewed 2026-07-17.)_
