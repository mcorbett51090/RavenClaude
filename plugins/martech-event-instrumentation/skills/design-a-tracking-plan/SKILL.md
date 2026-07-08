---
name: design-a-tracking-plan
description: Turn product and business questions into an event tracking plan — derive the event taxonomy (object-action naming), the properties, the naming convention, the identity model (anonymousId → userId stitching), and the per-event spec table, captured as the contract instrumentation builds to. Reach for this when the user asks "what events should we track?", "how should we name these?", or "how do we stitch anonymous to known users?". Used by `event-taxonomy-architect` (primary).
---

# Skill: design-a-tracking-plan

> **Invoked by:** `event-taxonomy-architect` (primary). Also consulted by `instrumentation-engineer` to read the plan it builds to and kick gaps back.
>
> **When to invoke:** "what events should we track?"; "how should we name/model these events?"; "how do we stitch anonymous→known?"; "our taxonomy is a mess — clean it up"; any "design the tracking plan" request.
>
> **Output:** a tracking plan — the event taxonomy (object-action) + properties + naming convention + identity model + the per-event spec table, ready to hand to instrumentation.

## Procedure

1. **List the questions the data must answer first.** Capture the business/product questions ("what is activation?", "which channel converts?", "where's the funnel drop-off?"). Events are derived from questions — an event no question needs doesn't get tracked. This is the guard against tracking-everything sprawl.
2. **Derive the events, object-action.** For each question, name the events that answer it as `Object Action` (`Order Completed`, `Product Viewed`, `Signup Started`). Fix **one case** and a **controlled verb set** up front; write the convention down — it's the anti-sprawl contract.
3. **Model events vs properties.** Collapse variants into one event + properties: `Product Viewed {category, price, source}`, not `product_viewed_from_search`. Fewer well-propertied events beat an explosion. Type every property (string/number/bool/enum) and mark required vs optional.
4. **Design the identity model — before any event is finalized.** Decide: how `anonymousId` is generated, the `userId` you stitch to, the `alias`/merge rule on the anonymous→known transition, and where the identity graph lives. This is the hardest part and it goes first; retrofitting identity onto collected anonymous data is the classic un-fixable mess.
5. **Tag consent + PII per event.** Assign each event a consent category and flag any PII properties (with the lawful basis). The `instrumentation-engineer` gates collection on these; no PII property ships without a basis.
6. **Assign an owner + destinations per event.** Who owns the event's correctness, and where it routes (warehouse, ad platforms, tools). Ownerless events rot.
7. **Capture it in the templates.** Write the plan to [`../../templates/tracking-plan.md`](../../templates/tracking-plan.md) and any complex event to [`../../templates/event-schema-spec.md`](../../templates/event-schema-spec.md). This is the contract instrumentation builds to.

## Worked example

> User: "We're a B2C subscription app. We want to know activation, which channel converts, and why people churn. What should we track?"

- **Questions → events:** activation → `Account Created`, `Onboarding Step Completed {step}`, `First Value Reached`; channel → `{utm_*}` on `Account Created` + a server-side `Subscription Started {plan, mrr}`; churn → `Subscription Cancelled {reason}`, `Feature Used {feature}`.
- **Model:** one `Onboarding Step Completed` with a `step` property — **not** five bespoke events. One `Feature Used` with a `feature` enum.
- **Identity:** `anonymousId` set on first visit; `Identify(userId)` at `Account Created`; `alias(anonymousId → userId)` so pre-signup pageviews stitch to the account. Identity graph in the CDP + mirrored to the warehouse.
- **Consent/PII:** `Subscription Started` carries `mrr` (no PII); email stays in the `Identify` trait behind the `marketing` consent category, never in event properties.
- **Output:** the filled tracking-plan template + a spec for `Subscription Started` (the revenue event → server-side).

## Guardrails

- Never track from the UI inward — track from the **questions** inward. No question, no event.
- Enforce object-action naming + one case + a controlled verb set **before** the first event is written; sprawl is the #1 killer of analytics trust.
- Fewer well-propertied events; a new event per variant is a smell — model the object, vary the properties.
- **Design the identity model before finalizing the plan.** No plan ships without anonymous→known stitching decided.
- Consent category + PII flags are part of the schema, not an afterthought — see [`../../knowledge/event-instrumentation-patterns-2026.md`](../../knowledge/event-instrumentation-patterns-2026.md).
- The plan is the contract: if instrumentation wants an off-plan event, the plan changes here first — not an ad-hoc `track()`.
