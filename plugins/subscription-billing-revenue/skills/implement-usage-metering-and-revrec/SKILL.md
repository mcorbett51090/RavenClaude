---
name: implement-usage-metering-and-revrec
description: "Build the usage-metering pipeline and the revenue-recognition/reporting by traversing the build path (event ingestion with idempotency/dedup → aggregation windows → rating against the price → invoice-line reconciliation → ASC 606 rev-rec: five-step, performance obligations, deferred revenue → MRR/ARR/churn reporting), then return an idempotent auditable metering pipeline that reconciles to the invoice, the deferred-revenue schedule, and the MRR/ARR/NRR reporting — with billing kept separate from rev-rec. Reach for this when the user asks 'build our usage metering', 'make the invoice match actual usage', 'recognize revenue per ASC 606', or 'build MRR/ARR/churn reporting'. Usage metering must be idempotent, auditable, and reconcilable to the invoice, or the bill is a guess. Used by billing-implementation-engineer (primary) and billing-systems-architect."
---

# Skill: implement-usage-metering-and-revrec

> **Invoked by:** `billing-implementation-engineer` (primary — the metering pipeline + rev-rec + reporting build) and `billing-systems-architect` (for the metering/rating and ASC 606 rev-rec design).
>
> **When to invoke:** "build our usage-metering / rating pipeline"; "make the invoice match what customers actually used"; "recognize revenue per ASC 606"; "build the deferred-revenue schedule"; "build MRR / ARR / churn / net-revenue-retention reporting"; any "meter the usage and recognize the revenue" question.
>
> **Output:** an idempotent, auditable usage-metering & rating pipeline that reconciles to the invoice + the ASC 606 rev-rec mapping + the deferred-revenue schedule + MRR/ARR/churn/NRR reporting — with the billing and rev-rec ledgers kept separate.

## Procedure

1. **Ingest usage events idempotently — dedup at the door.** Every usage event carries an **idempotency key** (an event id, or a natural key like customer+resource+timestamp); persist raw events and **dedup** so a replay or a double-send can't double-bill. Raw events are the audit trail — never aggregate away the ability to trace an invoice line back to the events behind it. Traverse the metering branch in [`../../knowledge/subscription-billing-revenue-decision-tree.md`](../../knowledge/subscription-billing-revenue-decision-tree.md).
2. **Aggregate in replay-safe windows, and handle late/corrected events.** Aggregate deduped events into billing-period windows. Handle **late-arriving** events (a window that's already been rated) and **corrections** (a reversal or restatement) explicitly — via a correction event, not a silent overwrite — so the aggregate is reproducible and a re-run yields the same number. Non-idempotent aggregation is how bills drift from reality.
3. **Rate deterministically against the price.** Apply the price rules from the catalog model — **tiered (graduated vs volume)**, **per-unit**, included-quantity **pools + overage** — to the aggregate. Rating must be **deterministic and reproducible**: the same events + the same price = the same charge, every time. Pin the price version used so a mid-period price change doesn't silently re-rate history.
4. **Reconcile every invoice line to its metered events.** The non-negotiable check: each usage invoice line **ties back** to the deduped events and the rating that produced it, and the invoice total **reconciles** to the sum of rated usage. A meter you can't reconcile to the invoice makes the bill a guess — build the reconciliation as a first-class artifact, not an afterthought.
5. **Recognize revenue per ASC 606 — and separate it from billing.** Map to the **five steps** (contract → performance obligations → transaction price → allocate → recognize as satisfied). Build the **deferred-revenue schedule** (up-front billing recognized over the service period; usage recognized as consumed), and keep the **billing** ledger (invoiced/collected) **separate** from the **rev-rec** ledger (recognized). Revenue recognized ≠ cash collected — conflating them corrupts both. This is a **build, not accounting advice** — flag the ASC 606 treatment for a qualified accountant and carry a retrieval date.
6. **Build MRR/ARR and churn reporting from subscription events.** Compute **MRR/ARR movement** decomposed into **new / expansion / contraction / churn**, plus **gross & net churn** and **net-revenue-retention (NRR)** — from subscription and usage events, **reconciled to billing**. Define usage MRR carefully (a trailing/normalized figure, stated), and keep the definitions explicit so the numbers are auditable.
7. **Prove it with reconciliations.** End with the tie-outs: **meter-to-invoice** reconciliation, a replayed/corrected event does **not** double-bill, the **deferred-revenue** schedule ties billing to recognized revenue, and MRR movement reconciles to billing. Route the warehouse/transformation pipeline at scale to `analytics-engineering`; route ASC 606 treatment to the accountant.

## Worked example

> User: "Our usage bills don't match customer dashboards, and finance wants proper deferred revenue and NRR. Build it."

- **Ingestion:** usage events had no idempotency key → double-sends double-billed. Add an **event id + dedup** on ingest; persist raw events as the audit trail.
- **Aggregation:** move to **replay-safe** period windows; handle late events with a **correction event** (not an overwrite) so re-runs are stable.
- **Rating:** apply the **included-pool + overage** price deterministically, pinning the price version → the same events now always produce the same charge, matching the dashboard.
- **Reconciliation:** each invoice usage line ties to its deduped events; the invoice total reconciles to rated usage → the mismatch is closed.
- **Rev-rec:** two obligations — subscription (ratable, deferred-revenue schedule) and usage (recognized as consumed); **billing ledger ≠ rev-rec ledger**. *ASC 606 treatment flagged for the accountant (retrieved <date>).*
- **Reporting:** MRR movement (new/expansion/contraction/churn) + **NRR**, reconciled to billing → finance gets auditable numbers.

## Guardrails

- **Meter idempotently — dedup at ingest** — a replay or double-send must not double-bill.
- **Keep raw events as the audit trail** — never aggregate away the ability to trace an invoice line to its events.
- **Aggregation and rating must be reproducible** — same events + same pinned price = same charge; handle late/corrected events via correction events, not overwrites.
- **Every invoice line reconciles to its metered events** — an un-reconcilable meter makes the bill a guess.
- **Keep the billing and rev-rec ledgers separate** — revenue recognized ≠ cash collected; conflating them corrupts both.
- **State the MRR/ARR/NRR definitions** — usage MRR especially needs an explicit normalization so the numbers are auditable.
- Metering/rev-rec/reporting is **execution** (the `billing-implementation-engineer` owns it); the metering & ASC 606 architecture is **design** (`billing-systems-architect`) — keep the seam clean.
- This is **not** the warehouse/transformation pipeline at scale (that's `analytics-engineering`), and **not accounting, tax, or audit advice** — ASC 606 mechanics are volatile, carry a **retrieval date**, and are confirmed with a qualified accountant before booking. See [`../../knowledge/subscription-billing-revenue-patterns-2026.md`](../../knowledge/subscription-billing-revenue-patterns-2026.md).
