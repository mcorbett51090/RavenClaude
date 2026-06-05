---
name: tracking-plan-design
description: "Step-by-step guide for designing a product analytics tracking plan — event taxonomy, property schema conventions, identity stitching strategy, and the governance process to keep the plan as the source of truth."
---

# Tracking Plan Design

## When to Use This

Starting a new product analytics implementation, migrating from ad-hoc events to a governed schema, or auditing an existing tracking setup that has accumulated inconsistent event names and properties.

## Step 1 — Define the Event Taxonomy

Group events into three tiers to limit cardinality while covering all analysis needs:

| Tier | Purpose | Naming pattern | Examples |
|---|---|---|---|
| **Page/Screen views** | Navigation and funnel entry | `<noun>_viewed` | `checkout_viewed`, `settings_viewed` |
| **User actions** | Explicit intent | `<noun>_<past-tense-verb>` | `button_clicked`, `form_submitted`, `filter_applied` |
| **System events** | Backend/lifecycle | `<noun>_<past-tense-verb>` | `order_completed`, `subscription_upgraded`, `session_started` |

**Naming rules:**
- Snake case, lowercase, no camelCase.
- Past tense for completed actions (`order_completed`, not `complete_order`).
- Noun first, verb second — sorts logically in your analytics tool.
- No abbreviations — `user_id` not `uid`; `product_name` not `prod_nm`.

## Step 2 — Design the Property Schema

### Global Properties (on every event)

These properties must be present on all events. Define them once; your CDP or wrapper fires them automatically:

| Property | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 string | Client event time (UTC) |
| `session_id` | string (UUID) | Current session identifier |
| `anonymous_id` | string (UUID) | Pre-login identifier; set on first visit, persists |
| `user_id` | string or null | Set after authentication; null if anonymous |
| `platform` | enum: web, ios, android | Originating platform |
| `app_version` | string | Semver of the app |
| `experiment_ids` | string[] | Active experiment assignments at time of event |

### Event-Specific Properties

Each event has a set of typed, named properties:

```
order_completed
  order_id: string (UUID)           — unique order identifier
  revenue: number                    — in minor currency units (cents)
  currency: string (ISO 4217)        — e.g., "USD"
  item_count: integer
  payment_method: enum               — "card" | "paypal" | "apple_pay"
  coupon_applied: boolean
  coupon_code: string | null         — null if coupon_applied is false
```

## Step 3 — Identity Stitching Strategy

Define the canonical identity model before building:

```
State 1: Pre-login
  anonymous_id = UUID (set on first visit, stored in localStorage)
  user_id = null

State 2: Post-login / signup
  anonymous_id = same UUID (preserved)
  user_id = "<backend user id>"
  → fire `identify` call linking anonymous_id → user_id

State 3: Cross-device (optional)
  → fire `alias` call when user logs in on a new device
    alias: new anonymous_id → known user_id
```

The `identify` call is the stitching moment. Without it, pre-login funnel analysis is disconnected from post-login behavior.

## Step 4 — The Tracking Plan Document

Maintain as a spreadsheet or code (JSON Schema / Segment's Protocols / Amplitude's Taxonomy):

| Column | Example |
|---|---|
| Event name | `checkout_started` |
| Trigger | User clicks "Proceed to Checkout" |
| Platform | web, ios |
| Properties | `cart_value`, `item_count`, `has_promo_code` |
| Property types | number, integer, boolean |
| Required? | Yes, Yes, Yes |
| Owner | @checkout-team |
| Status | Active |
| Version | 1.0 |

## Step 5 — Governance Process

1. **All new events require a tracking plan entry before implementation** — no ad-hoc events deployed without review.
2. **Schema validation in CI** — use Segment Protocols, Amplitude Taxonomy, or a custom JSON Schema validator to reject events with missing required properties or wrong types in staging.
3. **Versioning** — bump the event version when properties are added or types change. Consumers should filter by version when doing cohort analysis.
4. **Quarterly audit** — run a query against your event stream for events not in the tracking plan; either retire them or add them to the plan.
5. **Owner per event** — the owning team is responsible for keeping the tracking plan entry current when the feature changes.

## Schema Validation Example (Node.js / Segment)

```typescript
// Define schema for checkout_started
const checkoutStartedSchema = z.object({
  cart_value: z.number().nonnegative(),
  item_count: z.number().int().positive(),
  has_promo_code: z.boolean(),
});

// Validate before track call
function trackCheckoutStarted(props: unknown) {
  const validated = checkoutStartedSchema.parse(props); // throws on invalid
  analytics.track('checkout_started', validated);
}
```

## Pitfalls

- Naming events as present-tense commands (`click_button`) — inconsistent and doesn't convey state; use past tense for completed actions.
- Using user-id as a metric label in product analytics — it's high-cardinality; use it as a dimension in event properties, not as a label.
- Not including `anonymous_id` before login — funnel analysis can't connect acquisition → signup.
- Letting engineers add events without a tracking plan entry — within 6 months the event stream is ungovernable.
- Versioning the event name instead of a version property (`checkout_started_v2`) — pollutes the taxonomy and breaks dashboards that use the old name.

## See Also

- [`../../agents/product-analytics-instrumentation-engineer.md`](../../agents/product-analytics-instrumentation-engineer.md) — tracking plan, event schema, and identity stitching
- [`../../agents/experimentation-architect.md`](../../agents/experimentation-architect.md) — experiment exposure events and the `experiment_ids` property
