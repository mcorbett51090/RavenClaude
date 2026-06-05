# Choose between parameter actions and set actions by what the user controls

**Status:** Pattern
**Domain:** Viz / interactivity
**Applies to:** `tableau`

---

## Why this exists

Parameter actions and set actions both respond to a user's click and change a
value that filters or modifies a calculation — but they control fundamentally
different things. A parameter holds a single scalar value (a number, a string,
a date) that any calculation can reference. A set holds a group of members
(one or more dimension values that are IN or OUT) that scopes an aggregation or
a filter. Using a parameter where a set is needed (or vice versa) produces a
dashboard that either can't multi-select, can't do relative IN/OUT calculations,
or requires a workaround calculated field where none should be needed.

## How to apply

Use this decision:

| User action | What they're controlling | Use |
|---|---|---|
| Clicking to set a single reference value (target date, benchmark, threshold) | Scalar | Parameter action |
| Clicking to highlight/compare one vs the rest | Scalar or binary group | Parameter action (single) or set action (IN/OUT) |
| Clicking to add/remove members from a comparison group (multi-select) | Set of dimension members | Set action |
| Clicking to scope a cohort for a cohort analysis | Set of dimension members | Set action |

**Parameter action example (single benchmark):**
```
// Calculated field using the parameter
[Sales] / [Parameter: Benchmark]
// Action: on click, update [Parameter: Benchmark] to the clicked region's sales
```

**Set action example (cohort comparison):**
```
// Calculated field using the set
IF [Selected Customers] THEN "Selected" ELSE "Other" END
// Action: on click, add clicked customers to [Selected Customers] set
```

**Do:**
- Use a set action when the user needs to select multiple members or when
  IN/OUT membership drives an aggregation.
- Use a parameter action when the user is setting a single reference or control
  value (a benchmark, a selected time period).
- Document in the tooltip or a dashboard caption what the click action does.

**Don't:**
- Use a parameter action for multi-select scenarios — parameters hold one value;
  the second click overwrites the first.
- Use a set action for a scalar reference value — it is more complex than a
  parameter for no benefit.
- Combine a set action and a parameter action that control the same sheet without
  documenting the interaction clearly.

## Edge cases / when the rule does NOT apply

- Filter actions are the right tool when the goal is to filter a target sheet to
  only the clicked value; neither a parameter nor a set action is needed.
- URL actions for external navigation are their own separate mechanism and
  don't interact with the parameter vs set decision.

## See also

- [`../agents/tableau-viz-engineer.md`](../agents/tableau-viz-engineer.md) — owns interactivity design
- [`./viz-actions-and-interactivity.md`](./viz-actions-and-interactivity.md) — the upstream rule on choosing between action types

## Provenance

Codifies the parameter-vs-set-action distinction from Tableau's action types
documentation `[verify-at-build]` and standard dashboard interactivity design
practice. House opinion #3 from `CLAUDE.md` §3 ("the deliverable is the question
answered, not the dashboard") — interactivity design follows the user's question.

---

_Last reviewed: 2026-06-05 by `claude`_
