# Pick the interactivity mechanism by intent, not by habit

**Status:** Pattern — match the interaction (filter action / highlight action / parameter / set action) to what the user is trying to *do*; reach past the default quick-filter only with a reason, but reach for the right mechanism deliberately.

**Domain:** Viz design / interactivity

**Applies to:** `tableau`

---

## Why this exists

"Make these views talk to each other" has four common, *non-interchangeable* answers, and choosing the wrong one produces a dashboard that technically responds but doesn't do what the user meant. A **filter action** removes non-matching marks from a target view (drill/scope down). A **highlight action** keeps everything visible but emphasizes the selection (keep context, draw the eye). A **parameter** lets the user swap a measure, axis, threshold, or Top-N (change *what* is shown, not *which rows*). A **set action** writes the selection into a set so calcs can branch on "in vs out of selection" (compare-selection-to-rest, proportional brushing, asymmetric drill). Defaulting everything to a quick filter, or using a filter action where a highlight was meant, is the interactivity equivalent of the wrong chart type — it fights the user's goal.

## How to apply

Name the user's goal, then map it:

```
"Click a region, drill the detail view to it"        -> FILTER ACTION
   (Dashboard -> Actions -> Filter; run on Select; target the detail sheet.)

"Click a line, keep all lines but make this one pop"  -> HIGHLIGHT ACTION
   (Run on Hover or Select; nothing is removed, context preserved.)

"Let the user choose the measure / Top-N / threshold" -> PARAMETER
   (Parameter + a calc or set that references it; swaps WHAT is shown.)

"Compare the selected items vs. everyone else /        -> SET ACTION
 keep a persistent selection that calcs react to"
   ( Set + Set Action; IF [In/Out Set] THEN ... drives the comparison.)
```

**Do:**
- Write the sentence "when the user does X, the dashboard should Y" before wiring any action.
- Prefer **filter/highlight actions** over many synchronized quick filters — they're cheaper and more discoverable.
- Use **set actions** for "selection vs rest" and proportional-brushing patterns that a filter can't express.
- Set the action's **clearing behavior** ("Show all values" vs "Exclude all values") deliberately — the deselect state is part of the design.

**Don't:**
- Stack high-cardinality quick filters where a single filter action would do (performance + clutter).
- Use a filter action when the user needs to *keep context* — that's a highlight.
- Drive a measure/threshold swap with duplicated sheets when one parameter is cleaner.

## Edge cases / when the rule does NOT apply

A simple, low-cardinality global slicer (a Region dropdown over a small extract) is a perfectly good quick filter — don't over-engineer it into an action. Parameter **actions** (write a clicked value into a parameter) blur the parameter/set boundary and are the right tool for "click to set the comparison baseline." Cross-database/blended sources can constrain which fields a filter action can target — confirm the field is available on the target before wiring. RLS or any *security*-bearing filter is never an interactivity choice — it's an access control and escalates to `ravenclaude-core/security-reviewer`.

## See also

- [`./viz-dashboard-performance-by-design.md`](./viz-dashboard-performance-by-design.md) — actions vs. high-cardinality quick filters on load cost
- [`./viz-chart-type-follows-the-question.md`](./viz-chart-type-follows-the-question.md) — interaction complements, never rescues, the wrong chart
- [`../knowledge/viz-calc-decision-trees.md`](../knowledge/viz-calc-decision-trees.md) — the interactivity-mechanism tree
- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns interactivity selection
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — when the "filter" is actually RLS
- Tableau Help: "Actions and dashboards" / "Set Actions" / "Parameter Actions" `[verify-at-build]`

## Provenance

Codifies the viz-engineer's "pick interactivity by intent" discipline (step 5) from [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) and the RLS-is-not-a-filter house opinion #6 in [`../CLAUDE.md`](../CLAUDE.md). Action and set-action semantics are documented Tableau behavior; menu wording re-verify `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
