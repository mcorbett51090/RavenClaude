# Rev-rec & dunning runbook — <product / company>

> Captured when building/operating the billing implementation: webhook idempotency, dunning recovery, usage-metering reconciliation, and revenue recognition. Pairs with
> [`billing-model-design-doc.md`](billing-model-design-doc.md) (the model/architecture side of the same system).
> **Not accounting, tax, or audit advice.** ASC 606 mechanics are volatile — carry a retrieval date and confirm treatment with a qualified accountant before booking.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Provider:** <Stripe Billing / Chargebee / Zuora / Recurly / Metronome> · **Status:** draft / live · **Review cadence:** <monthly>

## 1. Provider integration & webhooks (every event is at-least-once)
| Event | Handler | Dedup key | Idempotent? | Out-of-order handling |
|---|---|---|---|---|
| <subscription.created> | <...> | <event id> | <yes> | <reconcile to current object> |
| <subscription.updated> | <...> | <event id> | <yes> | <reconcile to current object> |
| <subscription.deleted> | <...> | <event id> | <yes> | <set absolute status, not decrement> |
| <invoice.payment_failed> | <...> | <event id> | <yes> | <triggers dunning §3> |

- **Event log:** <where replay history is persisted>
- **Replay test:** <a re-delivered webhook is a no-op — confirmed>

## 2. Reconciliation job (drift = 0 is the health metric)
- **Schedule:** <nightly / hourly>
- **Pulls:** <subscriptions · invoices · payments from the provider>
- **Compares to:** <the ledger>
- **Repairs:** <status drift · missed cancellations · undelivered webhooks>
- **Alert on:** <drift != 0>
- **Last run drift:** <count · resolved>

## 3. Dunning & failed-payment recovery (instrument it)
- **Retry schedule:** <soft declines: spaced retries over N days · hard declines: no retry, prompt new card>
- **Card account-updater:** <enabled? network updater>
- **Customer sequence:** <dunning emails / in-app · cadence>
- **Grace period:** <N days before downgrade>
- **Entitlement downgrade on final failure:** <fail-closed — confirmed>
- **Instrumentation:**
  | Metric | Current | Target |
  |---|---|---|
  | Recovery rate per retry | <%> | <%> |
  | Involuntary-churn rate | <%> | <%> |
  | Revenue recovered | <$> | <$> |

## 4. Usage metering & reconciliation (if usage-based / hybrid)
- **Ingestion:** <idempotency key · dedup · raw events persisted>
- **Aggregation:** <windows · late-event & correction handling (correction events, not overwrites)>
- **Rating:** <price rule · price version pinned>
- **Meter-to-invoice reconciliation:** <every line ties to metered events · total reconciles — last check result>

## 5. Revenue recognition (ASC 606 — accountant-verified)
- **Performance obligations:** <subscription · usage · services>
- **Recognition pattern:** <subscription ratable · usage as consumed>
- **Deferred-revenue schedule:** <up-front billing recognized over the period>
- **Billing ↔ rev-rec tie-out:** <billing ledger vs rev-rec ledger — reconciled?>
- *Confirm ASC 606 / IFRS 15 treatment with a qualified accountant (<retrieval date>).*

## 6. SaaS metrics reporting (state the definitions)
| Metric | Definition used | Current |
|---|---|---|
| MRR / ARR | <normalized run-rate · usage-MRR normalization stated> | <$> |
| MRR movement | new / expansion / contraction / churn | <$ each> |
| Net revenue retention (NRR) | <your definition> | <%> |
| Gross / net churn | <your definition> | <%> |
- **Reconciled to billing?** <yes / no>

## 7. Control / audit loop (what proves it)
- <webhook-vs-provider drift = 0>
- <a replayed/corrected event does not double-bill>
- <deferred-revenue schedule ties billing to recognized revenue>
- <dunning recovery rate trending to target>

## Seams (not this team)
- **Pricing strategy / price points:** pricing-monetization
- **Payment rails / PSP / ledger code:** fintech-payments-engineering
- **FP&A / the P&L plan:** finance
- **Analytics warehouse / transformation pipeline:** analytics-engineering
- **Accounting entries / ASC 606 treatment / audit:** a qualified accountant / auditor

## Open questions / risks
- <list>

**Sign-off:** <billing eng lead / controller> · <date> · *Not accounting/tax/audit advice — ASC 606 treatment confirmed with a qualified accountant (<retrieval date>).*
