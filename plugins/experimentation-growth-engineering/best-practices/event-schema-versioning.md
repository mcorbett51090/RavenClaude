# Version event schemas explicitly; never silently change a property type

**Status:** Absolute rule
**Domain:** Product analytics / schema governance
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

An analytics event schema is a contract between the instrumentation layer and
every downstream consumer: funnels, retention models, experiment metric
calculations, and data warehouse tables all depend on stable property names and
types. A silent schema change (renaming `order_total` to `total_amount`, or
changing a string `user_id` to an integer) breaks every downstream query without
a compile-time error — the breakage surfaces days or weeks later as wrong numbers
in a dashboard or a missing funnel step. Schema versioning and a migration
protocol prevent silent schema rot.

## How to apply

**Naming a change:** when a property must change, add a new property alongside
the old one with a version indicator. Do NOT remove or rename the old property
in the same release.

```javascript
// Schema change migration — parallel properties pattern
analytics.track("order_completed", {
  // Old property — keep until all consumers have migrated
  order_total: 4999,          // deprecated — remove after 2026-09-01

  // New property — added in v2
  order_total_cents: 4999,    // v2: always integer cents
  order_total_currency: "USD",

  schema_version: 2,          // explicit version for downstream filtering
});
```

**Schema registry:** maintain a schema definition file (JSON Schema, Avro, or
Protobuf) committed to the repo for every event. PRs that add or change an event
must update the schema definition and bump the `schema_version`.

**Deprecation window:** keep old properties for a defined deprecation window
(typically 1–2 sprint cycles, enough for all consumers to migrate). Delete only
after verifying no downstream queries reference the old property name.

**Do:**
- Bump `schema_version` on every property addition or semantic change.
- Add new properties alongside old ones during the migration window.
- Validate events against the schema definition in CI (emit a warning or error
  on schema violations before they reach production).

**Don't:**
- Rename or change the type of an existing property in place.
- Delete a property without a deprecation window and consumer migration.
- Change a property's semantic meaning without a version bump (e.g. changing
  `revenue` from gross to net without renaming it).

## Edge cases / when the rule does NOT apply

- Brand-new events with no existing consumers (first-week instrumentation):
  freely restructure until the first consumer depends on the schema, then lock.
- Properties that have never been consumed by any analysis: safe to remove
  immediately; verify via `grep` + warehouse query before deleting.

## See also

- [`../agents/product-analytics-instrumentation-engineer.md`](../agents/product-analytics-instrumentation-engineer.md) — owns schema governance
- [`./instrumentation-is-a-designed-schema.md`](./instrumentation-is-a-designed-schema.md) — the tracking plan is the canonical schema definition
- [`./one-definition-per-event.md`](./one-definition-per-event.md) — schema versioning requires a single canonical definition per event

## Provenance

Standard event-schema governance practice. The parallel-properties migration
pattern is the recommended approach in Segment and RudderStack documentation
`[verify-at-use]`. The silent-type-change failure mode is a documented analytics
data quality issue in major product analytics platform guides.

---

_Last reviewed: 2026-06-05 by `claude`_
