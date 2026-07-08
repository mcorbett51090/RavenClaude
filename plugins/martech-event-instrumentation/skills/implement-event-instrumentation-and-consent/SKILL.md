---
name: implement-event-instrumentation-and-consent
description: Implement a tracking plan as working event collection — typed client/server-side Track/Identify calls, a codegen'd tracking library, schema validation in CI, consent gating at the source (Google Consent Mode v2 / IAB TCF / GPC), destination + reverse-ETL wiring, then QA the live stream. Reach for this when the user asks "implement these events", "add schema validation to CI", "wire consent", or "why is this event missing/wrong?". Used by `instrumentation-engineer` (primary).
---

# Skill: implement-event-instrumentation-and-consent

> **Invoked by:** `instrumentation-engineer` (primary). Consulted by `event-taxonomy-architect` to confirm a plan is implementable on the chosen CDP.
>
> **When to invoke:** "implement these events"; "add schema validation to CI"; "wire consent (Consent Mode / TCF / GPC)"; "set up destinations / reverse ETL"; "why is this event missing / duplicated / wrong?"; any turn-the-plan-into-working-collection request.
>
> **Output:** typed tracking calls + a CI schema-validation gate + consent gating at the source + destination/reverse-ETL wiring, QA'd against the tracking plan.

## Procedure

1. **Load the plan as the contract.** Read [`../../templates/tracking-plan.md`](../../templates/tracking-plan.md) and the per-event specs ([`../../templates/event-schema-spec.md`](../../templates/event-schema-spec.md)). An event not in the plan doesn't get a `track()` call — kick gaps back to the `event-taxonomy-architect` rather than inventing them.
2. **Codegen a typed tracking library from the plan.** Generate types + call wrappers (Avo / Segment Typewriter-style) so the plan and code can't drift — never hand-write stringly-typed `track('...')`. See [`../../knowledge/event-instrumentation-patterns-2026.md`](../../knowledge/event-instrumentation-patterns-2026.md).
3. **Place each event client- vs server-side per the plan.** Server-side (`Track` from the backend / a server-side CDP source) for revenue/conversion and anything ITP/ad-blockers drop; client-side for UI-context events; wire both for hybrid. Say when you'd move an event server-side for accuracy.
4. **Wire identity exactly as designed.** `Identify(userId, traits)` on known, `alias`/merge on the anonymous→known transition, a stable `anonymousId`. Don't invent stitching the plan didn't specify. Keep PII in traits behind a consent category — out of event properties.
5. **Add schema validation to CI.** Generate a schema (JSON Schema / the tracking-library types) from the plan and add a CI gate that fails the PR on an off-plan or mis-typed event. This is the point of catching bad events — cheap at the PR, expensive in the warehouse.
6. **Gate consent at the source.** Wire Google **Consent Mode v2** (ad_storage / analytics_storage signals), honor **IAB TCF** strings where applicable, and respect the **GPC** signal — gating collection *before* the event fires, per the event's consent category. Minimize PII (no raw email/name in properties without a lawful basis).
7. **Wire destinations + reverse ETL, then QA the live stream.** Configure destinations and reverse-ETL activation (Hightouch / Census); then run the QA pass — the CDP debugger / live view, a schema diff vs the plan, and a dedup/identity check — before declaring done. What lands in the debugger is the truth, not the code.

## Worked example

> User: "The tracking plan is approved. Implement `Subscription Started` and `Product Viewed` on Segment, and stop malformed events from shipping."

- **Codegen:** run Typewriter/Avo against the plan → a typed `Analytics.subscriptionStarted({plan, mrr})` and `Analytics.productViewed({category, price, source})`; no raw string calls.
- **Placement:** `Subscription Started` is revenue → **server-side** `Track` from the billing service (ITP-resilient, can't be ad-blocked); `Product Viewed` is UI context → **client-side**.
- **Identity:** `Identify(userId)` + traits at signup; `alias(anonymousId→userId)` so pre-signup `Product Viewed` events stitch.
- **CI validation:** a Protocols/JSON-Schema check in CI fails the PR if `mrr` is missing or a string.
- **Consent:** client-side collection gated behind Consent Mode v2 `analytics_storage`; email stays a trait behind the `marketing` category, never a property.
- **QA:** Segment debugger confirms both events land, schema matches the plan, no duplicate `Subscription Started` on ret/refresh.

## Guardrails

- Instrument to the plan — **no off-plan `track()` calls**; a gap is a change to the plan (architect), not an ad-hoc event.
- Typed tracking library, always — a stringly-typed call is a data-quality bug waiting to ship.
- Revenue/conversion events go **server-side**; client-only for those loses data to ITP/ad-blockers.
- **Schema validation in CI**, not a downstream dbt test days later — catch the bad event at the PR.
- Consent is gated **at collection**, not toggled at the destination; no PII property without a lawful basis + category.
- **QA the live stream** (debugger + schema diff + dedup check) before calling it done — trust what lands, not the code.
- Volatile claims (SDK APIs, Consent Mode versions, destination behavior) carry a **retrieval date** and are re-verified before shipping.
