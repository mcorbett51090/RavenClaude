---
name: design-billing-model-and-catalog
description: "Design the subscription billing model by traversing the billing decision tree (packaging shape: flat/tiered/per-seat/usage/hybrid → plan & product catalog model (product vs price vs plan vs entitlement) → proration & lifecycle rules → build-vs-buy → billing-platform selection → entitlement architecture → ASC 606 rev-rec architecture), then return the catalog model, the proration/lifecycle rules, the platform decision, the entitlement design, and the rev-rec mapping — with the migration cost and the conditions that flip it. Reach for this when the user asks 'model our plans/catalog', 'build billing or use Stripe/Chargebee/Zuora?', 'how should entitlements work?', or 'how do we recognize revenue?'. A wrong plan model is a migration, not a config change. Used by billing-systems-architect (primary) and billing-implementation-engineer."
---

# Skill: design-billing-model-and-catalog

> **Invoked by:** `billing-systems-architect` (primary, for the model/platform/rev-rec design) and `billing-implementation-engineer` (to confirm the architecture before building against it).
>
> **When to invoke:** "model our subscription plans and product catalog"; "flat, tiered, per-seat, usage, or hybrid — how do we express it?"; "build billing in-house or use Stripe Billing / Chargebee / Zuora / Recurly / Metronome?"; "how should entitlements / feature-gating work?"; "how do we recognize revenue (ASC 606)?"; any "how do we model the billing system" question.
>
> **Output:** the plan & product catalog model + the proration/lifecycle rules + the build-vs-buy & platform decision + the entitlement architecture + the ASC 606 rev-rec architecture + the migration cost and the 1-2 conditions that flip it.

## Procedure

1. **Name the packaging shape first — it drives the whole model.** Classify how the product is sold: **flat** (fixed price per period), **tiered** (graduated — each unit priced by the tier it falls in; vs volume — all units priced at the reached tier), **per-seat** (price × quantity, with add/remove-seat proration), **usage-based** (metered consumption × a rate), or **hybrid** (a platform fee + usage, or seats + overage). Most real systems are hybrid — design for it.
2. **Model the catalog as four separate concepts — don't collapse them.** **Product** (what is sold, the sellable thing) ≠ **Price** (how it's charged — amount, interval, tier/usage rules, currency) ≠ **Plan / Subscription** (what a specific customer holds, with quantity and status) ≠ **Entitlement** (what that subscription lets them use — features, limits, meters). Collapsing price into product, or entitlement into plan, is exactly the mistake that becomes a migration when packaging changes. Traverse the catalog branch in [`../../knowledge/subscription-billing-revenue-decision-tree.md`](../../knowledge/subscription-billing-revenue-decision-tree.md).
3. **Design the proration & lifecycle rules before integration.** Decide **plan-change** behavior: upgrades apply **now** (prorated credit + charge), downgrades usually at **period end** (avoid refunds); **trial→paid** conversion; **quantity** changes (per-seat proration); **coupon/discount** stacking and expiry; **cancellation** (immediate vs end-of-period) and reactivation. These rules are data-shaped — retrofitting them is a migration, so specify them up front.
4. **Decide build-vs-buy on coverage, not pride.** Buy the recurring-billing engine unless a hard constraint forbids it — you're really buying the long tail (**proration, tax/VAT, invoicing, dunning, PCI scope, compliance**). Build only what the platform can't express (bespoke metering/rating, complex entitlements, unusual proration). Name the coverage gaps and the migration cost of the choice.
5. **Select the platform provider-neutrally, matched to the model.** Map the requirements to categories, not brands: seat/tiered subscription engines (Stripe Billing, Chargebee, Recurly), enterprise/complex-catalog + rev-rec (Zuora), usage-metering-native (Metronome, and metering layers). Pick on catalog complexity, usage-metering needs, tax/invoicing coverage, rev-rec support, and migration cost — and name the flip conditions.
6. **Design the entitlement architecture — source of truth, propagation, enforcement.** Decide where entitlements **live** (the billing system vs a dedicated entitlements service), how they **propagate** (subscription event → entitlement update, or pulled at check time), and the **enforcement point** (API gateway / app / feature flag). Entitlements must be **derivable from subscription state** and **fail closed**.
7. **Map the revenue-recognition architecture to ASC 606, and separate the ledgers.** Walk the **five steps** (identify the contract → performance obligations → transaction price → allocate to obligations → recognize as satisfied), design **deferred-revenue** treatment (bill up front, recognize over the service period), and keep the **billing** ledger (invoiced/collected) separate from the **rev-rec** ledger (recognized). This is **architecture, not accounting advice** — carry a retrieval date and route treatment to a qualified accountant.
8. **State the flip conditions** — the 1-2 facts that change the model/platform/rev-rec call (e.g., "if usage becomes the primary meter, a metering-native platform beats the seat-billing incumbent"; "if we sell multi-element bundles, ASC 606 allocation and the catalog both get materially harder").

## Worked example

> User: "We're a B2B SaaS moving from flat per-seat to seats + usage overage, and we want proper revenue recognition. Model it and tell us whether to keep our home-grown billing."

- **Packaging:** **hybrid** — a per-seat platform fee + **usage overage** (API calls over an included pool) → the model must express seats *and* a metered rate.
- **Catalog:** Product (the SaaS) → Prices (a per-seat recurring price + a usage price with an included quantity + overage rate) → Subscription (seats held, status) → Entitlement (feature set + the included-usage pool). Keep the usage price separate so the pool/overage can change without touching the seat price.
- **Proration/lifecycle:** seat add = immediate proration; seat removal = credit at period end; usage rated at period close; trial→paid converts the seat price, usage starts metering at conversion.
- **Build-vs-buy:** the home-grown engine handles flat seats but has **no metering, no tax engine, no dunning** — the coverage gap is large → **buy**. Migration cost: re-map existing subscriptions + backfill.
- **Platform:** a subscription engine with a usage-metering layer (or a metering-native platform) — pick on the overage-metering fidelity and tax coverage.
- **Rev-rec:** two performance obligations (seat access recognized ratably; usage recognized as consumed); deferred revenue on the up-front seat billing; billing ledger ≠ rev-rec ledger. *Flag ASC 606 treatment for the accountant (retrieved <date>).*
- **Flip condition:** if usage revenue passes ~40% of the total, re-evaluate for a metering-native primary platform.

## Guardrails

- **Model the plan catalog before naming a platform or writing integration** — a wrong plan model is a migration, not a config change.
- **Keep product / price / plan / entitlement as four separate concepts** — collapsing them is the classic migration trap.
- **Specify proration & lifecycle rules up front** — they're data-shaped, so retrofitting them is a migration.
- **Build-vs-buy is a coverage question** — the long tail (proration, tax, invoicing, dunning, PCI, compliance) is what you're buying; build only what the platform can't express.
- **Entitlements are derived from subscription state and fail closed** — never a hand-maintained side table.
- **Keep the billing and rev-rec ledgers separate** — revenue recognized ≠ cash collected.
- Modeling the catalog/platform/rev-rec is **architecture** (the `billing-systems-architect` owns it); building it is **execution** (the `billing-implementation-engineer`) — keep the seam clean.
- This is **not** pricing strategy (that's `pricing-monetization`), payment-rail code (`fintech-payments-engineering`), or FP&A (`finance`); and **not accounting, tax, or audit advice** — ASC 606 & tax specifics carry a **retrieval date** and are verified with a qualified accountant. See [`../../knowledge/subscription-billing-revenue-patterns-2026.md`](../../knowledge/subscription-billing-revenue-patterns-2026.md).
