# Meet WCAG 2.2 AA as a floor, not an add-on

**Status:** Absolute rule
**Domain:** Dashboard accessibility
**Applies to:** `data-platform`

---

## Why this exists

Confirmed directly against this plugin's own two app starters (FORGE dashboard-top1pct P1-8,
2026-09-03): `agents/dashboard-builder.md` claimed WCAG 2.1 AA compliance and
`knowledge/dashboard-visual-craft-2026.md` declared a WCAG 2.2 floor — two different numbers
for one plugin — and neither starter met either one. `grep -rnE 'aria-[a-z]+|role=' templates/
cube-*-dashboard-starter` returned zero matches before this fix, with a positive control
(`tenant_id` returning 5 files) proving the probe could see the tree. The error state used
color alone (`<Text color="rose">`) with no icon or text cue, which fails WCAG 2.2's
Use-of-Color criterion regardless of contrast ratio. A dashboard that "looks done" and fails a
screen-reader or keyboard-only walkthrough is not done — accessibility is a floor every widget
clears, not a pass applied after the fact.

## How to apply

Pick **WCAG 2.2 AA** — it is a superset of 2.1, and this plugin's own knowledge file already
argued for it. Every widget in a shipped dashboard needs:

- **Live regions on data that updates without a page navigation** — `role="status"` +
  `aria-live="polite"` on a KPI value or chart that resolves after an async fetch, so a screen
  reader announces the update instead of staying silent.
- **A text alternative for every chart** — an SVG chart has no accessible text content on its
  own. `role="img"` + `aria-label` summarizing what the chart shows (metric, date range, point
  count) at minimum; a visually-hidden `<table>` with the same rows the chart renders visually
  is the fuller fallback for a screen-reader user who needs the actual values, not just a
  summary.
- **Error and status signaling that never relies on color alone** — pair a color change with an
  icon (`⚠`, marked `aria-hidden="true"` since the adjacent text already carries the meaning) or
  text. `role="alert"` on an error container so assistive tech announces it immediately.
- **Visible focus indicators on every interactive element** — a dashboard's custom-styled
  buttons/cards are a common place for a default focus ring to get silently stripped by a CSS
  reset. If a widget has no interactive elements at all (this plugin's starter KPI cards and
  charts, as shipped, are read-only), this bullet is vacuously satisfied — don't invent
  interactivity just to exercise it, but revisit the moment a real engagement adds a
  click-to-drill-down or an export button.
- **200%-zoom reflow without loss of content or function** (WCAG 2.2 Reflow) — verify a dense
  KPI grid doesn't require horizontal scrolling at 200% zoom on a standard viewport.

## Do

- Treat this the same as the cross-boundary denial test: no accessibility floor met, no merge.
- Assert `aria-`/`role=` coverage **per starter** when a plugin ships more than one app
  scaffold — a union check across multiple trees can pass with only one of them actually fixed.
- Add an `axe-core` assertion to the CI smoke pass (this plugin's `validate-data-platform-
  starters.yml`), asserting zero serious/critical violations, per starter.

## Don't

- Claim a WCAG level compliant in a docblock or a knowledge file without a mechanical check
  (grep for `aria-`/`role=`, or an axe-core run) backing the claim — this rule exists because
  that exact gap shipped in this plugin's own starters.
- Signal an error or a delta (increase/decrease) with color alone — always pair with an icon,
  text, or shape.
- Skip the visually-hidden table/summary for a chart on the theory that "the numbers are also
  in the KPI cards" — a chart's shape (trend, seasonality, outliers) is information the KPI
  cards don't carry, and a screen-reader user is entitled to it too.

## See also

- [`../agents/dashboard-builder.md`](../agents/dashboard-builder.md) — the agent that generates
  these components and now names WCAG 2.2 AA as the single floor
- [`../knowledge/dashboard-visual-craft-2026.md`](../knowledge/dashboard-visual-craft-2026.md) —
  §5 "Accessibility is a floor, not polish" — the dashboard-specific *application* of this rule
- [`./dashboard-provenance-on-every-widget.md`](./dashboard-provenance-on-every-widget.md) — the
  sibling absolute rule this same FORGE phase found under-satisfied alongside this one

## Provenance

Codifies the reconciled WCAG 2.2 AA floor across `agents/dashboard-builder.md`,
`templates/dashboard-engagement-checklist.md`, and `knowledge/dashboard-visual-craft-2026.md` —
FORGE dashboard-top1pct P1-8, 2026-09-03. Implemented directly in both app starters'
`KpiCard.tsx`/`RevenueChart.tsx` in the same change.

---

_Last reviewed: 2026-09-03 by `claude`_
