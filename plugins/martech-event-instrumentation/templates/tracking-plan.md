# Tracking plan — <product / surface>

> The **event contract**. This is the single source of truth the `instrumentation-engineer` builds to — an event not in this plan does not get a `track()` call. Pairs with
> [`event-schema-spec.md`](event-schema-spec.md) (the per-event detail for complex events).

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **CDP / collection:** <Segment / RudderStack / Snowplow / warehouse-first · client / server / hybrid> · **Status:** draft / approved / instrumented

## Questions the data must answer

- <business/product question 1 — e.g. "what is activation?">
- <question 2 — e.g. "which channel converts?">
- <question 3 — e.g. "why do users churn?">

## Naming convention (the anti-sprawl contract)

- **Event format:** `Object Action` (e.g. `Order Completed`), **case:** <Title Case / snake_case — pick ONE>.
- **Controlled vocabulary:** objects = <list> · verbs = <Created, Started, Completed, Viewed, Updated, Deleted, …>.
- **Property naming:** <snake_case / camelCase — pick ONE>, typed and consistent across events.

## Identity model

- **anonymousId:** <how generated / where stored>
- **userId:** <what you stitch to — the stable known-user key>
- **alias / merge rule:** <how the anonymous→known transition links pre-signup activity>
- **Identity graph lives:** <CDP-native / resolved in the warehouse>

## Event table (the contract)

| Event (Object Action) | Trigger (when it fires) | Key properties (name:type, * = required) | Identity call | Client / server | Destinations | Consent category | PII? | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| <Account Created> | <on signup success> | <plan:string*, source:string> | Identify + alias | server | warehouse, HubSpot | product | no | <name> | planned |
| <Product Viewed> | <on product page load> | <category:string*, price:number, source:enum> | — | client | warehouse | analytics | no | <name> | planned |
| <Subscription Started> | <on first successful charge> | <plan:string*, mrr:number*> | Identify | server | warehouse, ad platforms | marketing | no | <name> | planned |

> Status legend: `planned` → `instrumented` → `validated in CI` → `QA'd in stream`.

## Consent & PII summary

- **Consent categories in use:** <analytics / marketing / functional / …> and which events map to each.
- **PII policy:** no raw PII (email/name/phone) in event **properties**; PII lives in `Identify` traits behind a consent category with a lawful basis of <basis>.
- **Signals honored:** <Consent Mode v2 / IAB TCF / GPC>.

## Seams (who consumes these events)

- **dbt transforms:** analytics-engineering
- **A/B tests / growth:** experimentation-growth-engineering
- **Campaign activation:** marketing-operations
- **Org privacy / DSAR:** data-governance-privacy
- **Warehouse / BI:** data-platform

## Open questions / risks

- <list>

**Sign-off:** <reviewer> · <date>
