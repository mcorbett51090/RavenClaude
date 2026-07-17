# Billing model design doc — <product / company>

> The artifact captured when designing the subscription billing model & system. Pairs with
> [`revrec-and-dunning-runbook.md`](revrec-and-dunning-runbook.md) (the operate/recover/recognize side of the same system).
> **Not accounting, tax, or audit advice.** Volatile ASC 606 / tax / provider-API specifics carry a retrieval date — verify at use with a qualified accountant.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Reporting currency:** <e.g. USD> · **Status:** draft / approved · **Review cadence:** <per packaging change>

## 1. Packaging shape (name it first)
- **Shape:** <flat · per-seat · tiered (graduated / volume) · usage-based · hybrid (fee + usage / seats + overage)>
- **Why this shape:** <what the pricing-monetization strategy requires this billing system to express>

## 2. Plan & product catalog model (four separate concepts)
| Concept | Design | Notes |
|---|---|---|
| **Product** | <the sellable thing(s)> | stable identity |
| **Price** | <amount · interval · currency · tier/usage rules · included pool + overage> | changes without touching product |
| **Plan / Subscription** | <prices held · quantity · status · dates> | per-customer state |
| **Entitlement** | <features · limits · meters> | derived from subscription, fail-closed |

- **Migration risk:** <what a future packaging change would cost given this model — a wrong model is a migration>

## 3. Proration & lifecycle rules
- **Upgrade:** <now, prorated — credit unused + charge remainder>
- **Downgrade:** <at period end / immediate>
- **Seat/quantity change:** <add = immediate proration · remove = credit at period end>
- **Trial → paid:** <with/without card · conversion behavior · usage metering starts when>
- **Coupons/discounts:** <stacking · expiry · base vs usage>
- **Cancellation / reactivation:** <immediate vs end-of-period>

## 4. Build vs buy & platform
- **Decision:** <build · buy>
- **Coverage the platform must provide:** <proration · tax/VAT · invoicing · dunning · PCI · rev-rec>
- **Platform (provider-neutral):** <subscription engine (Stripe Billing / Chargebee / Recurly) · enterprise (Zuora) · metering-native (Metronome) — WHY>
- **Coverage gaps to build:** <bespoke metering / complex entitlements / unusual proration>
- **Migration cost:** <re-map subscriptions · backfill · cutover plan>

## 5. Entitlement architecture
- **Source of truth:** <billing system · dedicated entitlements service>
- **Propagation:** <event-driven · pull at check time · cache + invalidation>
- **Enforcement point:** <gateway · app · feature flag>
- **Fail-closed:** <unknown/stale entitlement denies access — confirmed>

## 6. Usage metering & rating (if usage-based / hybrid)
- **Meters:** <what is metered · unit · idempotency key>
- **Pipeline:** ingestion (dedup) → aggregation (windows · late/correction handling) → rating (price version pinned) → invoice line
- **Reconciliation:** <every invoice line ties to metered events · total reconciles to rated usage>

## 7. Revenue-recognition architecture (ASC 606 — accountant-verified)
- **Performance obligations:** <subscription access · usage · services — distinct?>
- **Transaction price & allocation:** <incl. variable consideration · standalone selling prices>
- **Recognition pattern:** <subscription ratable · usage as consumed>
- **Deferred revenue:** <up-front billing recognized over the period — the billing↔rev-rec bridge>
- **Ledger separation:** <billing ledger separate from rev-rec ledger — confirmed>
- *Confirm ASC 606 / IFRS 15 treatment with a qualified accountant (<retrieval date>).*

## 8. Flip conditions (what changes the model/platform/rev-rec call)
- <e.g. usage revenue passes ~40% of total → re-evaluate for a metering-native primary platform>
- <e.g. multi-element bundles added → ASC 606 allocation and the catalog get materially harder>

## Seams (not this team)
- **Pricing strategy / packaging economics / price points:** pricing-monetization
- **Payment rails / PSP / card-network & ledger code:** fintech-payments-engineering
- **FP&A / budgeting / the P&L plan:** finance
- **Analytics warehouse / transformation pipeline:** analytics-engineering
- **Accounting entries / ASC 606 treatment / audit:** a qualified accountant / auditor

## Open questions / risks
- <list>

**Sign-off:** <billing architect / eng lead> · <date> · *Not accounting/tax/audit advice — volatile ASC 606 / tax / provider specifics verified at use (<retrieval date>).*
