# Render in the viewer's locale and the tenant's timezone — never the server's

**Status:** Absolute rule
**Domain:** Dashboard internationalization / timezone correctness
**Applies to:** `data-platform`

---

## Why this exists

Confirmed directly against this plugin (FORGE dashboard-top1pct P2-15, 2026-09-03): zero files
mentioned i18n, localization, or RTL before this phase, and the concrete defect was already
shipped — `grep -rn '"en-US"' templates/cube-*` returned exactly 2 hits, one per starter's
`KpiCard.tsx`, both hard-coding `new Intl.NumberFormat("en-US", …)`. Locale is the visible half of
this gap; timezone is the higher-stakes half. A multi-tenant dashboard whose "today" is the
**server's** today silently misreports every tenant outside that zone — a "last 30 days" window
computed in the server's local time can be off by a full day at either boundary for a tenant in a
different zone, and nothing about a wrong number *looks* wrong. `P1-8`'s provenance-footer
discipline made date ranges visible; a date range with no named timezone is not real provenance,
because "last 30 days" means a different 30 days depending on which clock computed it.

## How to apply

- **Locale drives number/date formatting; timezone drives what data a query actually returns.**
  These are two different problems that happen to travel together — don't conflate "the app looks
  right in French" with "the app computed the right 30-day window for a tenant in Paris." Both
  matter; only the second one silently corrupts the underlying numbers.
- **Timezone must reach the semantic-layer query, not just the rendering layer.** Formatting a
  UTC-computed date range into a tenant's local time *after* the query already ran using the
  wrong window doesn't fix anything — the window itself was wrong. Cube's REST API takes a
  top-level `timezone` field on the query object (an IANA zone, e.g. `"America/Los_Angeles"`) —
  every timezone-sensitive query must set it explicitly. An unset `timezone` silently defaults to
  UTC, which is the warehouse-UTC fork below, not a neutral no-op.
- **Name the timezone in the provenance footer.** `P1-8`'s absolute provenance rule
  (source + date range + comparison baseline) is not satisfied by a bare date range once more
  than one timezone is in play — `"last 30 days"` needs a `"(America/New_York)"` alongside it, or
  the range is ambiguous to whoever reads the widget later.
- **Pick a resolution strategy for locale + timezone and document which fork you took** — see
  [`knowledge/dashboard-timezone-decision-2026.md`](../knowledge/dashboard-timezone-decision-2026.md)
  for the three real options (tenant-configured, viewer-browser, warehouse-UTC) and why there is
  no universally right answer. Whichever fork an engagement takes, the resolved `{locale,
  timezone}` pair should reach every widget through one shared context, not be re-derived
  per-component (a per-component derivation is how one KPI card ends up in a different timezone
  than its neighbor).
- **RTL is a layout concern distinct from locale/timezone correctness** — a dashboard doesn't need
  full RTL support to satisfy this rule, but it should not *break* when `dir="rtl"` is set (a
  smoke check, not a certification). Don't conflate "we format numbers in the viewer's locale"
  with "we support RTL layout" — they're different bars, and claiming the second because you did
  the first is a false equivalence this rule specifically rejects.

## What "good" looks like

- Every `Intl.NumberFormat`/`Intl.DateTimeFormat` call in the dashboard reads its locale from a
  shared context, never a hard-coded BCP-47 string.
- Every timezone-sensitive Cube query sets an explicit `timezone` field sourced from that same
  context.
- The provenance footer names the timezone alongside the date range.
- A test renders a widget under a non-default locale/timezone (e.g. `de-DE` /
  `Europe/Berlin`) and asserts both the number format AND the date-range boundary change — proving
  the timezone reaches the query, not just the display.

## Related

- [`knowledge/dashboard-timezone-decision-2026.md`](../knowledge/dashboard-timezone-decision-2026.md) —
  the tenant-configured / viewer-browser / warehouse-UTC fork.
- [`dashboard-set-data-freshness-slas.md`](./dashboard-set-data-freshness-slas.md) — provenance
  discipline this rule extends with a timezone requirement.
- [`dashboard-meet-the-accessibility-floor.md`](./dashboard-meet-the-accessibility-floor.md) — the
  other absolute rule that shares the "looks done, isn't" failure shape this one guards against.
