# Instrument funnels at decision points, not page views

**Status:** Pattern
**Domain:** Product analytics / instrumentation
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

A funnel built from page-view events ("visited checkout", "visited confirmation")
conflates users who saw a page with users who made a decision on that page. The
result is a funnel drop-off rate that is technically accurate but practically
unactionable: you cannot tell from page-view events whether a user bounced
because they saw the form and left, or because they never scrolled to the CTA,
or because they hit an error. Decision-point events ("checkout_initiated",
"payment_method_selected", "order_confirmed") reveal the actual intent signals
where product changes have leverage.

## How to apply

For each funnel step, identify the **decision point** — the observable action
that indicates a user has intentionally progressed, not merely arrived:

| Page view (not enough) | Decision point (instrument this) |
|---|---|
| Visited /checkout | `checkout_initiated` (clicked "Proceed to checkout") |
| Visited /payment | `payment_method_selected` (selected a payment method) |
| Visited /confirm | `order_confirmed` (clicked "Place order") |

Each decision-point event should carry:
- `user_id` / `anonymous_id`
- `session_id`
- `funnel_id` and `step_name` (for cross-funnel joining)
- Timestamp
- Any variant assignment relevant to the step

**Do:**
- Fire the event at the moment of intentional action (click, submit, select),
  not on page mount.
- Keep one event name per funnel step; don't create `checkout_started_v2` when
  you can version the schema.
- Include the funnel id so steps from different funnels don't collide in analysis.

**Don't:**
- Use `page_view` or `screen_view` events as funnel steps — they don't represent
  decisions.
- Fire the event before the user's action resolves (e.g. before the API confirms
  the order) — fire on confirmed state change, not optimistic UI.
- Instrument only the happy path; instrument abandonment events too
  (e.g. `checkout_abandoned`) to close the funnel.

## Edge cases / when the rule does NOT apply

- Landing-page top-of-funnel: the "decision" IS arrival at the page for users
  coming from an ad or email; a page-view event is appropriate here as the
  entry event.
- Scroll-depth or time-on-page engagement metrics: page-view variants are
  correct for these (they ARE the behaviour of interest).

## See also

- [`../agents/product-analytics-instrumentation-engineer.md`](../agents/product-analytics-instrumentation-engineer.md) — owns funnel instrumentation design
- [`./instrumentation-is-a-designed-schema.md`](./instrumentation-is-a-designed-schema.md) — decision-point events must conform to the tracking plan schema
- [`./one-definition-per-event.md`](./one-definition-per-event.md) — each funnel step has exactly one canonical event definition

## Provenance

Standard product analytics and funnel-analysis practice. The decision-point
instrumentation model is the recommended approach in product analytics
tooling documentation (Amplitude, Mixpanel, PostHog patterns). Routes to
`applied-statistics` for funnel significance analysis.

---

_Last reviewed: 2026-06-05 by `claude`_
