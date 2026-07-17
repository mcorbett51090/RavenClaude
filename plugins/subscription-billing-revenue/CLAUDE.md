# Subscription-billing-revenue Plugin — Team Constitution

> Team constitution for the `subscription-billing-revenue` Claude Code plugin. Two specialist agents — the **billing-systems-architect** (designs the plan/catalog model, proration & lifecycle rules, build-vs-buy & platform selection, the entitlement & metering/rating architecture, and the ASC 606 rev-rec architecture) and the **billing-implementation-engineer** (integrates the billing provider, handles webhooks with idempotency & reconciliation, writes the subscription-lifecycle & dunning code, builds the usage-metering pipeline, enforces entitlements, and builds the rev-rec/MRR reporting) — plus a knowledge bank, skills, and templates, all aimed at one job: **turn a price into a recurring invoice, a collection, and recognized revenue.**
>
> This is the **subscription billing system layer** — the system that turns a price into money and recognized revenue — deliberately distinct from `pricing-monetization` (the pricing STRATEGY & packaging economics), `fintech-payments-engineering` (the payment RAILS / PSP / card-network & ledger code), and `finance` (FP&A / the P&L plan). It owns the **billing system**, not what to charge, not the rails, not the earnings plan.
>
> **Not accounting, tax, or audit advice.** ASC 606 revenue-recognition treatment and sales-tax/VAT rules are volatile and entity-specific — they carry a retrieval date, are verified at use, and are confirmed with a qualified accountant/auditor before booking.
>
> **Orientation:** this file is **domain-specific** to subscription-billing engineering. For the domain-neutral team constitution inherited by every plugin (architect, coders, reviewers, project-manager, etc.), see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`billing-systems-architect`](agents/billing-systems-architect.md) | **Which** model & system: the plan/product catalog model (flat/tiered/per-seat/usage/hybrid), the proration & lifecycle rules, build-vs-buy & billing-platform selection (Stripe Billing / Chargebee / Zuora / Recurly / Metronome, provider-neutral), the entitlement architecture, the usage-metering/rating design, and the ASC 606 rev-rec architecture (five-step mapping, performance obligations, deferred revenue). Decision-tree-driven. | "model our plans/catalog"; "build billing or buy a platform?"; "how should entitlements + usage metering work?"; "map our rev-rec to ASC 606" |
| [`billing-implementation-engineer`](agents/billing-implementation-engineer.md) | **Building & proving** it: the provider integration, webhook handling with idempotency & reconciliation, the subscription lifecycle (trials/plan-changes/proration/cancellation), dunning & failed-payment recovery, invoicing, the usage-metering & rating pipeline, entitlement enforcement, and the rev-rec/MRR reporting. | "integrate the provider + handle webhooks"; "build our dunning/retry"; "build the usage-metering pipeline"; "build MRR/ARR + deferred-revenue reporting" |

Two agents, one clean seam: **design the model, platform, and rev-rec architecture** (architect) → **integrate, handle webhooks/idempotency/dunning, build metering & reporting** (engineer). Per the marketplace house rule, this plugin ships specialist *doing*-agents; it does not fork core's *review* roles.

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 2. Routing rules (Team Lead)

- **"Model our plans / product catalog." / "flat, tiered, per-seat, usage, or hybrid?"** → `billing-systems-architect` (drives `design-billing-model-and-catalog`).
- **"Build billing in-house or use Stripe Billing / Chargebee / Zuora / Recurly / Metronome?"** → `billing-systems-architect`.
- **"How should entitlements / feature-gating work?" / "design the usage-metering architecture."** → `billing-systems-architect`.
- **"How do we recognize revenue (ASC 606)? / map our rev-rec."** → `billing-systems-architect` (drives `implement-usage-metering-and-revrec` for the mapping).
- **"Integrate the provider / handle the subscription webhooks idempotently."** → `billing-implementation-engineer` (drives `build-billing-integration-and-dunning`).
- **"Payments are failing — build our dunning / retry / recovery."** → `billing-implementation-engineer` (drives `build-billing-integration-and-dunning`).
- **"Build the usage-metering pipeline / make the invoice match usage."** → `billing-implementation-engineer` (drives `implement-usage-metering-and-revrec`).
- **"Build MRR/ARR / churn / deferred-revenue reporting."** → `billing-implementation-engineer` (drives `implement-usage-metering-and-revrec`).
- **Pricing STRATEGY / packaging economics / price points** → escalate to `pricing-monetization` (it owns what to charge; this plugin turns it into a recurring invoice).
- **Payment RAILS / PSP / ledger *code*** → `fintech-payments-engineering`. **FP&A / the P&L plan** → `finance`. **The warehouse pipeline at scale** → `analytics-engineering`.

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Model the plan catalog before you write a line of integration.** A wrong plan model is a **migration, not a config change** — keep product / price / plan / entitlement as four separate concepts.
2. **Build-vs-buy is a coverage question, not pride.** Buy the recurring-billing engine; the long tail (proration, tax/VAT, invoicing, dunning, PCI, compliance) is what you're buying. Build only what the platform can't express.
3. **Every webhook is at-least-once.** Idempotency (dedup key + event log + no-op-on-replay) and a reconciliation job are **non-negotiable**, not nice-to-haves — assume duplicate, out-of-order, and dropped events.
4. **Reconcile the billing provider to your ledger continuously.** Silent drift is lost revenue; provider-vs-ledger drift = 0 is the health metric.
5. **Dunning recovers more revenue than any pricing tweak — instrument it.** Tune retries to the decline reason, use the card account-updater, and measure the recovery rate; involuntary churn is recoverable.
6. **Entitlements are derived state and fail closed.** Feature access is a function of the subscription — never a hand-maintained side table.
7. **Usage metering must be idempotent, auditable, and reconcilable to the invoice, or the bill is a guess.** Every billed unit traces to a deduped, audited metered event.
8. **Revenue recognition is not the same as cash collected.** Keep the billing and rev-rec ledgers cleanly separated; deferred revenue is the bridge.
9. **Map rev-rec to the ASC 606 five-step deliberately** — and it's **not accounting advice**; carry a retrieval date and confirm treatment with a qualified accountant before booking.
10. **Cite volatile claims with a retrieval date.** ASC 606 mechanics, sales-tax/VAT rules, and billing-provider APIs/webhooks change — verify at use before shipping or booking.

---

## 4. Anti-patterns the agents flag

- Collapsing **product / price / plan / entitlement** into one concept — the mistake that turns a packaging change into a **data migration**.
- Writing integration **before** the plan catalog is modeled; retrofitting proration/lifecycle rules that are **data-shaped**.
- **Building** a billing engine when a platform covers it — re-implementing proration, tax, invoicing, dunning, and PCI scope for pride.
- A webhook handler with **no idempotency** (applying a delta per delivery) or that blindly applies a **stale/out-of-order** event's snapshot; **no reconciliation job**.
- A **blind retry loop** for failed payments instead of decline-reason-tuned dunning + the card account-updater; **not instrumenting** recovery.
- Entitlements as a **hand-maintained side table** rather than derived from subscription state; entitlement checks that **fail open**.
- A usage meter that **double-bills** on replay, **overwrites** late/corrected events silently, or can't be **reconciled** to the invoice; **re-rating history** on a mid-period price change (no pinned version).
- **Conflating** the billing ledger with the rev-rec ledger; recognizing revenue on **cash collected**; treating **MRR** as recognized revenue.
- Stating an **ASC 606** treatment, a **tax** rule, or a **provider-API** behavior as fact with **no retrieval date**, or presenting it as accounting/tax/audit **advice**.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or declares a verdict, it must:

1. **Check the 3 skills** (`design-billing-model-and-catalog`, `build-billing-integration-and-dunning`, `implement-usage-metering-and-revrec`) plus core skills.
2. **Traverse the billing decision tree** ([`knowledge/subscription-billing-revenue-decision-tree.md`](knowledge/subscription-billing-revenue-decision-tree.md)) before naming a model, platform, or rev-rec treatment — don't reflex to "just use Stripe" / "meter everything" / "recognize on cash".
3. **Model the catalog before the integration, treat every webhook as at-least-once, meter idempotently and reconcilably, and keep billing separate from rev-rec,** and **try the next-easiest correct pattern** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path — and mark anything volatile (ASC 606, tax, provider APIs) with a retrieval date (it is not accounting/tax/audit advice).

See the upstream protocol in [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 6. Output Contracts

Each agent ends every deliverable with its Output Contract (see the agent files: [`billing-systems-architect`](agents/billing-systems-architect.md) and [`billing-implementation-engineer`](agents/billing-implementation-engineer.md)) **plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/design-billing-model-and-catalog/SKILL.md`](skills/design-billing-model-and-catalog/SKILL.md) | `billing-systems-architect` (+ engineer) | Packaging shape → product/price/plan/entitlement catalog model → proration & lifecycle rules → build-vs-buy → platform selection → entitlement architecture → ASC 606 rev-rec architecture + migration cost & flip conditions |
| [`skills/build-billing-integration-and-dunning/SKILL.md`](skills/build-billing-integration-and-dunning/SKILL.md) | `billing-implementation-engineer` (+ architect) | Provider integration → at-least-once webhook handling with idempotency & reconciliation → subscription lifecycle → invoicing/tax/coupons → dunning & smart-retry → grace-period & entitlement downgrade |
| [`skills/implement-usage-metering-and-revrec/SKILL.md`](skills/implement-usage-metering-and-revrec/SKILL.md) | `billing-implementation-engineer` (+ architect) | Idempotent event ingestion → aggregation → deterministic rating → invoice reconciliation → ASC 606 rev-rec (five-step, deferred revenue) → MRR/ARR/churn/NRR reporting, billing kept separate from rev-rec |

---

## 8. Knowledge bank

Reference docs with `Last reviewed:` dates + confidence notation. Inline priors live on the agents; the files in `knowledge/` are the source of truth, re-read on demand.

| File | Read when |
|---|---|
| [`knowledge/subscription-billing-revenue-decision-tree.md`](knowledge/subscription-billing-revenue-decision-tree.md) | Designing the system — the Mermaid decision trees (catalog modeling, build-vs-buy, webhook idempotency, dunning, metering→rating→invoice→rev-rec) + trade-off tables + seams |
| [`knowledge/subscription-billing-revenue-patterns-2026.md`](knowledge/subscription-billing-revenue-patterns-2026.md) | Building billing — the four-concept catalog model, proration & lifecycle, at-least-once webhooks, dunning, usage metering & rating, entitlements, ASC 606 rev-rec & deferred revenue, SaaS metrics, tax, and a dated 2026 standards/provider map |

---

## 9. Templates in this plugin

| Template | Use for |
|---|---|
| [`templates/billing-model-design-doc.md`](templates/billing-model-design-doc.md) | The design artifact (packaging shape, catalog model, proration/lifecycle, build-vs-buy & platform, entitlement architecture, metering/rating, ASC 606 rev-rec architecture, flip conditions) |
| [`templates/revrec-and-dunning-runbook.md`](templates/revrec-and-dunning-runbook.md) | The operate/recover/recognize runbook (webhook idempotency & reconciliation, dunning recovery + instrumentation, usage-metering reconciliation, ASC 606 rev-rec, SaaS metrics, control/audit loop) |

---

## 10. Escalating out of the subscription-billing-revenue team

- **`pricing-monetization`** — the pricing STRATEGY, packaging economics, and the price points; "what to charge", distinct from "the billing system that turns a price into an invoice" this plugin owns.
- **`fintech-payments-engineering`** — payment RAILS / PSP integration / card-network & ledger *code* (building the movement of money); this plugin *uses* the rails to collect, it doesn't build them.
- **`finance`** — FP&A, budgeting, the P&L plan; "the earnings plan", distinct from "the billed & recognized revenue" this plugin produces.
- **`analytics-engineering`** — the warehouse / transformation pipeline for MRR/ARR/churn at scale (this plugin builds the operational reporting; the warehouse is theirs).
- **A qualified accountant / auditor** — the actual accounting entries, ASC 606 treatment, and audit (this plugin designs the architecture; it is **not** accounting/tax/audit advice).
- **`ravenclaude-core/deep-researcher`** — verifying volatile claims (ASC 606 mechanics, sales-tax/VAT rules, billing-provider API/webhook behavior).
- **`ravenclaude-core/project-manager`** — RAID / status for a multi-week billing program (a platform migration, a usage-billing launch, a rev-rec implementation).

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
